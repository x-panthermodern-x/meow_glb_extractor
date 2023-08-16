import os
import struct
import json

def unpack_glb_to_directory(file_path):
    # Check if the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Create the directory to save extracted files
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_directory = os.path.join(os.path.dirname(file_path), f"{base_name} extracted")
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Read the GLB file in binary mode
    with open(file_path, "rb") as f:
        # Read the header
        magic, version, length = struct.unpack("<I2I", f.read(12))
        if magic != 0x46546C67:  # ASCII for "glTF"
            raise ValueError("File is not a valid GLB format")

        # Read the chunk headers and data
        chunks = []
        while f.tell() < length:
            chunk_length, chunk_type = struct.unpack("<I4s", f.read(8))
            chunk_data = f.read(chunk_length)
            chunks.append((chunk_type, chunk_data))

    # Extract textures
    textures = []
    if chunks[0][0] == b"JSON":
        json_data = json.loads(chunks[0][1].decode("utf-8"))
        if "images" in json_data:
            for idx, image in enumerate(json_data["images"]):
                if chunks[1][0] == b"BIN\x00":
                    buffer_view = json_data["bufferViews"][image["bufferView"]]
                    buffer_start = buffer_view["byteOffset"]
                    buffer_end = buffer_start + buffer_view["byteLength"]
                    texture_data = chunks[1][1][buffer_start:buffer_end]
                    texture_filename = os.path.join(output_directory, f"texture_{idx}.png")
                    with open(texture_filename, "wb") as texture_file:
                        texture_file.write(texture_data)
                    textures.append(texture_filename)

    # Extract mesh
    if "images" in json_data:
        del json_data["images"]
    if "textures" in json_data:
        del json_data["textures"]
    if "samplers" in json_data:
        del json_data["samplers"]
    if "materials" in json_data:
        del json_data["materials"]
    json_bytes = json.dumps(json_data).encode("utf-8")
    mesh_output_file_path = os.path.join(output_directory, "extracted_mesh.glb")
    with open(mesh_output_file_path, "wb") as f:
        f.write(struct.pack("<I2I", magic, version, 20 + 8 + len(json_bytes) + 8 + len(chunks[1][1])))
        f.write(struct.pack("<I4s", len(json_bytes), b"JSON"))
        f.write(json_bytes)
        f.write(struct.pack("<I4s", len(chunks[1][1]), b"BIN\x00"))
        f.write(chunks[1][1])

    return textures, mesh_output_file_path

# Extract textures and mesh to a specific directory
extracted_textures, extracted_mesh_path = unpack_glb_to_directory("./64dd106558f50a12df4a46b4.glb")
extracted_textures, extracted_mesh_path



