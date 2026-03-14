"""Strip target_features custom sections from wasm objects inside .a archives.

This is needed when libraries are compiled with a newer Emscripten (e.g. 5.0.2)
but linked in an older Emscripten environment (e.g. 3.1.58 used by Pyodide).
The newer compiler embeds feature flags (bulk-memory-opt, call-indirect-overlong)
that the older wasm-opt doesn't recognize.

Approach: rewrite each .a archive, processing each wasm .o member to remove
the target_features custom section. Uses pure Python archive parsing to avoid
ar compatibility issues across platforms.
"""

import sys
import os


# Features not supported by older wasm-opt (Emscripten 3.1.58)
FEATURES_TO_STRIP = {b'bulk-memory-opt', b'call-indirect-overlong'}


def read_leb128(data, pos):
    """Read an unsigned LEB128 value."""
    value = 0
    shift = 0
    while pos < len(data):
        byte = data[pos]
        pos += 1
        value |= (byte & 0x7f) << shift
        shift += 7
        if not (byte & 0x80):
            break
    return value, pos


def write_leb128(value):
    """Encode an unsigned LEB128 value."""
    result = bytearray()
    while True:
        byte = value & 0x7f
        value >>= 7
        if value:
            byte |= 0x80
        result.append(byte)
        if not value:
            break
    return result


def filter_target_features(section_payload: bytes) -> bytes | None:
    """Remove unsupported features from a target_features section payload.

    Returns filtered payload, or None if section should be kept as-is.
    The payload starts AFTER the section name.
    """
    pos = 0
    count, pos = read_leb128(section_payload, pos)

    features = []
    for _ in range(count):
        prefix = section_payload[pos:pos + 1]
        pos += 1
        name_len, pos = read_leb128(section_payload, pos)
        name = section_payload[pos:pos + name_len]
        pos += name_len
        features.append((prefix, name))

    filtered = [(p, n) for p, n in features if n not in FEATURES_TO_STRIP]
    if len(filtered) == len(features):
        return None  # Nothing changed

    # Rebuild payload
    result = bytearray()
    result.extend(write_leb128(len(filtered)))
    for prefix, name in filtered:
        result.extend(prefix)
        result.extend(write_leb128(len(name)))
        result.extend(name)
    return bytes(result)


def patch_target_features(wasm_bytes: bytes) -> bytes:
    """Remove unsupported features from target_features in a wasm binary."""
    if len(wasm_bytes) < 8 or wasm_bytes[:4] != b'\x00asm':
        return wasm_bytes

    result = bytearray(wasm_bytes[:8])  # magic + version
    pos = 8
    changed = False

    while pos < len(wasm_bytes):
        section_id = wasm_bytes[pos]
        pos += 1

        size, pos = read_leb128(wasm_bytes, pos)
        section_data = wasm_bytes[pos:pos + size]
        pos += size

        # Custom section (id=0): check if it's target_features
        if section_id == 0 and len(section_data) > 0:
            name_len, name_start = read_leb128(section_data, 0)
            if name_start + name_len <= len(section_data):
                name = section_data[name_start:name_start + name_len]
                if name == b'target_features':
                    payload_start = name_start + name_len
                    payload = section_data[payload_start:]
                    filtered = filter_target_features(payload)
                    if filtered is not None:
                        changed = True
                        # Rebuild section data: name_len + name + filtered_payload
                        new_section_data = (
                            section_data[:payload_start] + filtered
                        )
                        result.append(section_id)
                        result.extend(write_leb128(len(new_section_data)))
                        result.extend(new_section_data)
                        continue

        # Write section back unchanged
        result.append(section_id)
        result.extend(write_leb128(size))
        result.extend(section_data)

    return bytes(result) if changed else wasm_bytes


def process_archive(archive_path: str) -> None:
    """Strip target_features from all wasm objects in a Unix ar archive."""
    with open(archive_path, 'rb') as f:
        data = f.read()

    if not data.startswith(b'!<arch>\n'):
        print(f"Not an ar archive: {archive_path}")
        return

    # Parse ar archive and rewrite members
    pos = 8  # Skip magic
    members = []
    modified_count = 0

    # Read string table for long names (if present)
    string_table = b''

    while pos < len(data):
        # Each member header is 60 bytes
        if pos + 60 > len(data):
            break

        header = data[pos:pos + 60]
        name_raw = header[0:16]
        size_str = header[48:58].strip()
        magic = header[58:60]

        if magic != b'`\n':
            break

        size = int(size_str)
        member_data = data[pos + 60:pos + 60 + size]

        # Determine member name
        name = name_raw.rstrip()
        if name == b'//' or name == b'//':
            # String table for long names
            string_table = member_data
            members.append((header, member_data, False))
        elif name == b'/' or name == b'/':
            # Symbol table
            members.append((header, member_data, False))
        else:
            # Regular member - check if it's a wasm object
            is_wasm = len(member_data) >= 4 and member_data[:4] == b'\x00asm'
            if is_wasm:
                stripped = patch_target_features(member_data)
                if stripped is not member_data:
                    modified_count += 1
                    # Update size in header if changed
                    new_size = len(stripped)
                    new_header = (
                        header[:48]
                        + f'{new_size:<10d}'.encode()
                        + header[58:60]
                    )
                    members.append((new_header, stripped, True))
                else:
                    members.append((header, member_data, False))
            else:
                members.append((header, member_data, False))

        # Move to next member (padded to 2-byte boundary)
        pos += 60 + size
        if pos % 2 != 0:
            pos += 1

    if modified_count == 0:
        print(f"No features to strip in {archive_path}")
        return

    # Rebuild archive
    output = bytearray(b'!<arch>\n')
    for header, member_data, was_modified in members:
        output.extend(header)
        output.extend(member_data)
        if len(member_data) % 2 != 0:
            output.append(0x0a)  # Pad to even

    with open(archive_path, 'wb') as f:
        f.write(output)

    print(f"Patched target_features in {modified_count} objects in {archive_path}")


if __name__ == '__main__':
    for path in sys.argv[1:]:
        process_archive(path)
