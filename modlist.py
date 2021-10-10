import toml
import requests

from pathlib import Path
import time


class Modpack:
    def __init__(self, pack_path: Path):
        self.pack_dir = dir = pack_path.parent

        with open(pack_path) as f:
            self.pack = toml.loads(f.read())
        
        with open(Path(dir, self.pack["index"]["file"])) as f:
            self.index = toml.loads(f.read())
        
        self.mods = []
        for mod in self.index["files"]:
            with open(Path(dir, mod["file"])) as f:
                self.mods.append(toml.loads(f.read()))
        
        print(f"Loaded {len(self.mods)} mods")


class CurseAPI:
    BASE_URL = "https://addons-ecs.forgesvc.net/api/v2/addon/"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0"})

    def get_mod_info(self, addon_id):
        resp = self.session.get(CurseAPI.BASE_URL + str(addon_id))
        return resp.json()


if __name__ == "__main__":
    curse = CurseAPI()
    pack = Modpack(Path("pack.toml"))

    with open("modlist.html", "wb+") as f:
        f.write("""
        <html>
        <head>
            <title>Modlist</title>
            <meta charset="UTF-8">
            <style>
                body {
                    margin:40px auto;
                    max-width: 650px;
                    line-height: 1.6;
                    font-size: 18px;
                    color: #444;
                    background-color: #EEE;
                    padding:0 10px;
                }

                h1, h2, h3 {
                    line-height:1.2;
                }

                img.thumb {
                    width: 64px;
                    height: 64px;
                    display: inline;
                }

                h3.mod_name {
                    margin-left: 8px;
                }

                div.mod_header {
                    display: flex;
                    align-content: center;
                }

                div.mod {
                    border-bottom: 2px solid #444;
                    margin-top: 1.5em;
                }
            </style>
        </head>
        """.encode())
        f.write("<body>".encode())
        for i, mod in enumerate(pack.mods):
            info = curse.get_mod_info(mod["update"]["curseforge"]["project-id"])
            missing_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAUElEQVQ4jWOMiIj4z0ABYKJEMwiwoAssX74cr4bIyEgUPvVdgMsmXC6jvgvQbSbZAGRAKEAZaBqIyACftyh2AW2TMigQCQXkIPcCQcDAwAAALuUUMutW5tIAAAAASUVORK5CYII="
            thumbnail = [a for a in info['attachments'] if a['isDefault']]
            if not thumbnail:
                thumbnail = missing_image
            else:
                thumbnail = thumbnail[0]['url']
            f.write(f"""
            <div id={info['id']} class='mod'>
                <a href='{info['websiteUrl']}'>
                    <div class='mod_header'>
                        <img class='thumb' src='{thumbnail}' alt='{info['name']}' />
                        <h3 class='mod_name'>{info['name']}</h3>
                    </div>
                </a>
                <p class='mod_desc'>{info['summary']}</p>
            </div>
            """.encode())
            print(f"Writing mod {i+1} of {len(pack.mods)}")
            time.sleep(0.1)
        f.write("</body></html>".encode())


