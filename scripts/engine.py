import os
import re

def main():
    issue_title = os.getenv("ISSUE_TITLE", "")
    if not issue_title.startswith("tttp:"):
        return

    move = issue_title.split(":")[1].split(",")
    row, col = int(move[0]), int(move[1])

    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    # Link exato que está no seu README
    user_link = f"https://github.com/MoreiraGabryel/MoreiraGabryel/issues/new?title=tttp:{row},{col}"
    user_pattern = rf"\[ \]\({re.escape(user_link)}\)"

    # Se achar o espaço vazio, coloca o X
    if re.search(user_pattern, content):
        content = re.sub(user_pattern, "❌", content)
        
        # Jogada da IA (Simples para teste: pega o próximo vago)
        ia_prioridades = ["1,1", "0,0", "0,2", "2,0", "2,2", "0,1", "1,0", "1,2", "2,1"]
        for pos in ia_prioridades:
            ia_link = f"https://github.com/MoreiraGabryel/MoreiraGabryel/issues/new?title=tttp:{pos}"
            ia_pattern = rf"\[ \]\({re.escape(ia_link)}\)"
            if re.search(ia_pattern, content):
                content = re.sub(ia_pattern, "⭕", content)
                break

    # Atualiza o status
    if "[ ]" not in content:
        status_msg = "**Status:** Fim de jogo. `eu sempre ganho 🤖`"
    else:
        status_msg = "**Status:** Sua vez!"

    content = re.sub(r"\*\*Status:\*\*.*", status_msg, content)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    main()
