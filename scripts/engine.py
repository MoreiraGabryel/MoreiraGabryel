import os
import re

def main():
    issue_title = os.getenv("ISSUE_TITLE", "")
    if not issue_title.startswith("tttp:"): return

    try:
        coords = issue_title.split(":")[1].split(",")
        row, col = int(coords[0]), int(coords[1])
    except: return

    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    user_move_link = rf"\[ \]\(https:\/\/github\.com\/MoreiraGabryel\/MoreiraGabryel\/issues\/new\?title=tttp:{row},{col}\)"
    
    if re.search(user_move_link, content):
        content = re.sub(user_move_link, "❌", content)
        
        ia_patterns = [r"tttp:1,1", r"tttp:0,0", r"tttp:0,2", r"tttp:2,0", r"tttp:2,2"]
        for p in ia_patterns:
            ia_move_link = rf"\[ \]\(https:\/\/github\.com\/MoreiraGabryel\/MoreiraGabryel\/issues\/new\?title={p}\)"
            if re.search(ia_move_link, content):
                content = re.sub(ia_move_link, "⭕", content)
                break

    if "[ ]" not in content:
        status_update = "**Status:** Fim de jogo.\n> **Mensagem do Sistema:** `EU SEMPRE VENÇO`"
    else:
        status_update = "**Status:** Sua vez!\n> **Mensagem do Sistema:** *Aguardando sua derrota...*"

    content = re.sub(r"\*\*Status:\*\*.*", status_update, content, flags=re.DOTALL)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    main()
