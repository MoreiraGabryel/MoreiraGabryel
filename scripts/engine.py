import os
import re

def main():
    issue_title = os.getenv("ISSUE_TITLE", "")
    if not issue_title.startswith("tttp:"):
        return

    move = issue_title.split(":")[1].split(",")
    row_u, col_u = int(move[0]), int(move[1])

    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    
    user_pattern = rf"\[ \]\(https:\/\/github\.com\/MoreiraGabryel\/MoreiraGabryel\/issues\/new\?title=tttp:{row_u},{col_u}\)"
    content = re.sub(user_pattern, "❌", content)

    status_msg = "**Status:** Fim de jogo.\n> **Mensagem do Sistema:** `EU SEMPRE VENÇO`"
    
    # 3. Atualizar o Status no README
    content = re.sub(r"\*\*Status:\*\*.*", status_msg, content)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    main()
