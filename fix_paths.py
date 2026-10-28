import re, pathlib
for p in pathlib.Path("ml/models").glob("*.py"):
    b = p.read_bytes()
    n = re.sub(rb"model_asset_path=(\w+)", rb'model_asset_buffer=open(\1, "rb").read()', b)
    if n != b:
        p.write_bytes(n)
        print("da sua:", p)
