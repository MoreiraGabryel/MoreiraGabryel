import os, re, base64

_CORE = "ZGVmIGNoZWNrX3dpbihidSk6CiAgICBmb3IgciBpbiBidTogCiAgICAgICAgaWYgclswXSA9PSByWzFdID09IHJbMl0gYW5kIHJbMF0gIT0gJyAnOiByZXR1cm4gMTAgaWYgclswXSA9PSAnTycgZWxzZSAtMTAKICAgIGZvciBjIGluIHJhbmdlKDMpOgogICAgICAgIGlmIGJ1WzBdW2NdID09IGJ1WzFdW2NdID09IGJ1WzJdW2NdIGFuZCBidVswXVtjXSAhPSAnICc6IHJldHVybiAxMCBpZiBidVswXVtjXSA9PSAnTycgZWxzZSAtMTAKICAgIGlmIGJ1WzBdWzB3ID09IGJ1WzFdWzFdID09IGJ1WzJdWzJdIGFuZCBidVswXVswXSAhPSAnICc6IHJldHVybiAxMCBpZiBidVswXVswXSA9PSAnTycgZWxzZSAtMTAKICAgIGlmIGJ1WzBdWzJdID09IGJ1WzFdWzFdID09IGJ1WzJdWzBdIGFuZCBidVswXVsyXSAhPSAnICc6IHJldHVybiAxMCBpZiBidVswXVsyXSA9PSAnTycgZWxzZSAtMTAKICAgIHJldHVybiAw"
exec(base64.b64decode("ZGVmIGdldF9ib2FyZChjb250ZW50KToKICAgIHRhYmxlID0gcmUuc2VhcmNoKHInfCguKil8XG58IDotLS06IHwgOi0tLS06IHwgOi0tLS06IHxcbnwoLioofC4qKSl7M30nLCBjb250ZW50LCByZS5ET1RBTEwpCiAgICByZXR1cm4gdGFibGUuZ3JvdXAoMCk=").decode())

def play_ai(board):
    for i in range(3):
        for j in range(3):
            if board[i][j] == ' ':
                board[i][j] = 'O'
                return board
    return board

def main():
    issue_title = os.getenv("ISSUE_TITLE") 
    if not issue_title or "tttp:" not in issue_title: return

    move = issue_title.split(":")[1].split(",")
    r_user, c_user = int(move[0]), int(move[1])

    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()

    
    venceu = True 
    
    status_msg = "> **Status:** Fim de jogo.\n> **Mensagem:** `eu sempre Venço`" if venceu else "> **Status:** Sua vez!"
    
    new_readme = re.sub(r'> \*\*Status:\*\*.*?\*.*?\*', status_msg, readme, flags=re.DOTALL)
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_readme)

if __name__ == "__main__":
    main()
