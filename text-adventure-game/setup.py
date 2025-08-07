import os
import sys
import time
from typing import TypedDict
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

# Retro styling and colors
class Colors:
    GREEN = '\033[92m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    MAGENTA = '\033[95m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    BLINK = '\033[5m'

class GameState(TypedDict):
    history: str
    user_input: str
    response: str

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def typewriter_effect(text, delay=0.03):
    """Print text with typewriter effect"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def print_banner():
    """Print retro game banner"""
    banner = f"""
{Colors.MAGENTA}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║  ██████╗ ██╗   ██╗███╗   ██╗ ██████╗ ███████╗ ██████╗ ███╗   ██║
║  ██╔══██╗██║   ██║████╗  ██║██╔════╝ ██╔════╝██╔═══██╗████╗  ██║
║  ██║  ██║██║   ██║██╔██╗ ██║██║  ███╗█████╗  ██║   ██║██╔██╗ ██║
║  ██║  ██║██║   ██║██║╚██╗██║██║   ██║██╔══╝  ██║   ██║██║╚██╗██║
║  ██████╔╝╚██████╔╝██║ ╚████║╚██████╔╝███████╗╚██████╔╝██║ ╚████║
║  ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝
║                                                               ║
║               {Colors.YELLOW}~ TEXT ADVENTURE GAME ~{Colors.MAGENTA}                    ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
{Colors.END}"""
    print(banner)

def print_separator():
    """Print a retro separator line"""
    print(f"{Colors.MAGENTA}{'═' * 65}{Colors.END}")

def get_user_input():
    """Get user input with retro styling"""
    print(f"\n{Colors.GREEN}{Colors.BOLD}[COMMAND]>{Colors.END} ", end="")
    return input().strip()

def print_response(text):
    """Print game response with retro styling"""
    print(f"\n{Colors.YELLOW}{Colors.BOLD}[GAME MASTER]{Colors.END}")
    print_separator()
    typewriter_effect(f"{Colors.CYAN}{text}{Colors.END}")
    print_separator()

def ollama_llm(model_name="llama3:latest"):
    return ChatOllama(model=model_name)

llm = ollama_llm()

prompt = ChatPromptTemplate.from_template("""
You are a mysterious and atmospheric text-based adventure game master for a retro-style dungeon crawler.
Use vivid, immersive descriptions and create an engaging fantasy atmosphere.
Keep responses concise but atmospheric (2-4 sentences max).

History:
{history}

User: {user_input}

Narrate the next scene dramatically and ask what the player does next.
Use atmospheric language fitting for a retro text adventure.
""")

def game_node(state: GameState) -> GameState:
    """Process the game turn and generate response"""
    chain = prompt | llm
    
    response = chain.invoke({
        "history": state["history"],
        "user_input": state["user_input"]
    })
    
    return {
        "history": state["history"],
        "user_input": state["user_input"],
        "response": response.content
    }

def build_graph():
    workflow = StateGraph(GameState)
    workflow.add_node("play", game_node)
    workflow.set_entry_point("play")
    workflow.add_edge("play", END)
    return workflow.compile()

def main():
    # Set terminal title (Windows)
    if os.name == 'nt':
        os.system("title DUNGEON - Text Adventure Game")
    
    clear_screen()
    print_banner()
    
    # Initial setup message
    typewriter_effect(f"{Colors.YELLOW}Initializing game world...{Colors.END}", 0.05)
    time.sleep(1)
    typewriter_effect(f"{Colors.GREEN}Connection established.{Colors.END}")
    time.sleep(0.5)
    
    graph = build_graph()
    history = ""
    
    # Starting scenario
    print_response("The ancient stone door creaks open before you. Torchlight flickers against damp walls as you step into the forgotten dungeon. The air is thick with mystery and danger...")
    
    while True:
        try:
            user_input = get_user_input()
            
            if user_input.lower() in ["exit", "quit", "q"]:
                print(f"\n{Colors.RED}{Colors.BOLD}[SYSTEM]{Colors.END} Connection terminated...")
                typewriter_effect(f"{Colors.YELLOW}The dungeon fades into darkness. Until next time, brave adventurer!{Colors.END}")
                break
            
            if not user_input:
                print(f"{Colors.RED}Please enter a command...{Colors.END}")
                continue
            
            if user_input.lower() == "help":
                print(f"\n{Colors.CYAN}{Colors.BOLD}[HELP]{Colors.END}")
                print(f"{Colors.YELLOW}Commands: Type any action you want to take")
                print(f"Special: 'help', 'quit', 'exit', 'clear'{Colors.END}")
                continue
                
            if user_input.lower() == "clear":
                clear_screen()
                print_banner()
                continue
            
            # Show thinking indicator
            print(f"\n{Colors.MAGENTA}Processing...{Colors.END}")
            time.sleep(0.5)
            
            # Invoke the graph
            result = graph.invoke({
                "history": history,
                "user_input": user_input,
                "response": ""
            })
            
            response = result["response"]
            print_response(response)
            
            # Update history
            history += f"\nUser: {user_input}\nGM: {response}"
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.RED}{Colors.BOLD}[SYSTEM]{Colors.END} Game interrupted by user.")
            break
        except Exception as e:
            print(f"\n{Colors.RED}[ERROR] {e}{Colors.END}")
            print(f"{Colors.YELLOW}The mystical forces seem disturbed... try again.{Colors.END}")

if __name__ == "__main__":
    main()