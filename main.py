#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║              STELLIGHT AI PROTOTYPE v0.1                     ║
║         Advanced Neural Language Processing Engine           ║
╚══════════════════════════════════════════════════════════════╝
"""

import re
import sys
import time
import os
import random
import platform
import socket
import shutil
from memory import MemoryManager
from learn import KnowledgeEngine
from brain import DecisionBrain
from groq_provider import run_training_session

class Color:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'

class StellightEngine:
    def __init__(self, username="nexusly_inco", version="0.1"):
        self.user = username
        self.version = version
        self.start_time = time.time()
        self.memory = MemoryManager()
        self.knowledge = KnowledgeEngine()
        self.brain = DecisionBrain(self.memory, self.knowledge)
        self.provider = self.brain.provider
        self.session_learn_count = 0
        self.total_interactions = 0
        self.confidence_scores = []
        self.term_width = shutil.get_terminal_size((80, 24)).columns

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_centered(self, text, color=Color.WHITE, style=""):
        clean_text = re.sub(r'\033\[[0-9;]*m', '', text)
        padding = max(0, (self.term_width - len(clean_text)) // 2)
        print(f"{' ' * padding}{style}{color}{text}{Color.RESET}")

    def get_system_info(self):
        """Gather client/session data for the compact boot panel."""
        def safe(func, default="[REDACTED]"):
            try:
                return func()
            except Exception:
                return default

        mem = "[REDACTED]"
        if os.path.exists('/proc/meminfo'):
            try:
                with open('/proc/meminfo') as f:
                    for line in f:
                        if line.startswith('MemTotal:'):
                            mem_kb = int(line.split()[1])
                            mem = f"{mem_kb / 1024 / 1024:.1f} GiB"
                            break
            except OSError:
                pass

        started = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.start_time))
        session_id = hex(abs(hash(self.user + str(self.start_time))))[2:10]
        knowledge_count = len(getattr(self.knowledge, 'questions', []))
        history_count = len(self.memory.storage.get('history', []))
        columns = shutil.get_terminal_size((80, 24)).columns

        return [
            ("Client", self.user),
            ("Host", safe(lambda: socket.gethostname(), "localhost")),
            ("OS", f"{platform.system()} {platform.release()}"),
            ("Kernel", platform.version() or "[REDACTED]"),
            ("Machine", platform.machine() or "[REDACTED]"),
            ("CPU", platform.processor() or "[REDACTED]"),
            ("RAM", mem),
            ("Python", platform.python_version()),
            ("Terminal", f"{columns} columns"),
            ("Knowledge", f"{knowledge_count} learned prompts"),
            ("Memory", f"{history_count} saved turns"),
            ("Session", f"0x{session_id}"),
            ("Started", started),
        ]

    def _loading_splash(self):
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        deadline = time.time() + random.uniform(2.0, 4.0)
        i = 0
        while time.time() < deadline:
            dots = "." * ((i % 3) + 1)
            self.clear_screen()
            print(f"\n{Color.CYAN}{Color.BOLD}")
            self.print_centered("Starlight loading" + dots, Color.CYAN, Color.BOLD)
            self.print_centered(frames[i % len(frames)], Color.MAGENTA, Color.BOLD)
            print(Color.RESET)
            time.sleep(0.16)
            i += 1

    def _print_client_panel(self):
        info = self.get_system_info()
        label_width = max(len(label) for label, _ in info)
        value_width = min(max(len(str(value)) for _, value in info), max(32, self.term_width - label_width - 10))
        box_width = label_width + value_width + 7
        horizontal = '═' * (box_width - 2)

        self.print_centered(f"╔{horizontal}╗", Color.MAGENTA, Color.BOLD)
        title = "CLIENT INFORMATION"
        self.print_centered(f"║{title:^{box_width - 2}}║", Color.MAGENTA, Color.BOLD)
        self.print_centered(f"╠{horizontal}╣", Color.MAGENTA, Color.BOLD)
        for label, value in info:
            text = str(value)
            if len(text) > value_width:
                text = text[:value_width - 1] + "…"
            row = f"║ {label:<{label_width}} │ {text:<{value_width}} ║"
            self.print_centered(row, Color.MAGENTA)
        self.print_centered(f"╚{horizontal}╝", Color.MAGENTA, Color.BOLD)

    def _menu_choice(self):
        print(f"{Color.CYAN}{Color.BOLD}╔══ Starlight Mode ══╗{Color.RESET}")
        print(f"  {Color.GREEN}1){Color.RESET} Train the AI")
        print(f"  {Color.GREEN}2){Color.RESET} Chat with the AI")
        print(f"{Color.CYAN}{Color.BOLD}╚════════════════════╝{Color.RESET}")
        choice = input(f"\n{Color.CYAN}{Color.BOLD}  Choose 1 or 2:{Color.RESET} ").strip().lower()
        return "train" if choice in {"1", "train", "t"} else "chat"

    def _training_box(self, stats, frame=0):
        dots = [".  ", ".. ", "..."][frame % 3]
        width = 46
        lines = [
            f"Training{dots}  (Ctrl+C to stop)",
            f"Provider: {stats.get('provider', 'Groq')}",
            f"Information accumulated: {stats.get('learned', 0)}",
            f"Training cycles: {stats.get('topics', 0)}",
            f"Errors: {stats.get('errors', 0)} / 10",
            f"Status: {stats.get('status', 'training')}",
        ]
        if stats.get("last_question"):
            lines.append(f"Last: {stats['last_question']}")
        if stats.get("stop_reason") and stats.get("status") == "stopped":
            lines.append(f"Stopped: {stats['stop_reason']}")
        self.clear_screen()
        self.print_centered("╔" + "═" * width + "╗", Color.MAGENTA, Color.BOLD)
        for line in lines:
            self.print_centered("║ " + line[:width-2].ljust(width - 2) + " ║", Color.MAGENTA)
        self.print_centered("╚" + "═" * width + "╝", Color.MAGENTA, Color.BOLD)

    def train_ai(self):
        frame = {"i": 0}
        def progress(stats):
            self._training_box(stats, frame["i"])
            frame["i"] += 1
        initial = {"provider": "Groq", "learned": 0, "topics": 0, "errors": 0, "status": "training"}
        self._training_box(initial)
        stats = run_training_session(self.knowledge, self.provider, progress_callback=progress)
        self.brain.retrain_generator()
        self.session_learn_count += stats.get("learned", 0)
        self._training_box(stats, frame["i"])
        if stats.get("stop_reason") == "missing GROQ_API_KEY":
            print(f"\n{Color.RED}{Color.BOLD}  ✗ Set GROQ_API_KEY before real Groq training.{Color.RESET}")
        else:
            print(f"\n{Color.GREEN}{Color.BOLD}  ✓ Training stopped: {stats.get('stop_reason', 'manual stop')}.{Color.RESET}")
        print(f"{Color.DIM}  Press Enter to chat.{Color.RESET}")
        input()

    def boot_sequence(self):
        mode = self._menu_choice()
        if mode == "train":
            self.train_ai()
        self._loading_splash()

        boot_tasks = [
            ("Neural Core", "ready"),
            ("Memory", "synced"),
            ("NLP", "online"),
            ("Math Engine", "optimized"),
            ("Knowledge", "indexed"),
            ("Groq", "enabled" if self.provider.enabled else "env-missing"),
        ]

        bar_width = min(34, max(20, self.term_width - 42))
        for task, status in boot_tasks:
            for filled in range(bar_width + 1):
                bar = f"{Color.GREEN}{'█' * filled}{Color.DIM}{'░' * (bar_width - filled)}{Color.RESET}"
                sys.stdout.write(
                    f"\r  {Color.CYAN}[{bar}{Color.CYAN}] {Color.WHITE}{task:<14} {Color.YELLOW}{status:<10}{Color.RESET}"
                )
                sys.stdout.flush()
                time.sleep(0.012)
            time.sleep(0.08)
        time.sleep(0.25)

        # Clear the splash/progress UI so bars do not stack on screen.
        self.clear_screen()
        print()
        self._print_client_panel()
        print(f"\n{Color.CYAN}{Color.BOLD}  ✦ Welcome back, {self.user}{Color.RESET}")
        print(f"  {Color.DIM}Ready for chat, learning, and math. Type /help for commands.{Color.RESET}\n")

    def handle_system_commands(self, text):
        lower_text = text.lower()
        if lower_text in ["/help", "/?"]:
            print(f"\n{Color.CYAN}{Color.BOLD}╔══ Available Commands ══╗{Color.RESET}")
            commands = [
                ("learn [Q] | [A]", "Teach the AI a new question-answer pair"),
                ("remember my [attr] is [val]", "Store personal information"),
                ("/stats", "View session statistics"),
                ("/clear", "Clear the terminal screen"),
                ("/status", "Display system status"),
                ("/train", "Run the Groq/local training pass"),
                ("exit | quit | shutdown", "End the session"),
            ]
            for cmd, desc in commands:
                print(f"  {Color.GREEN}{cmd:<35}{Color.RESET} {Color.DIM}{desc}{Color.RESET}")
            print(f"{Color.CYAN}{Color.BOLD}╚════════════════════════╝{Color.RESET}\n")
            return True

        elif lower_text == "/stats":
            runtime = time.time() - self.start_time
            avg_conf = sum(self.confidence_scores) / len(self.confidence_scores) if self.confidence_scores else 0
            print(f"\n{Color.CYAN}{Color.BOLD}╔══ Session Statistics ══╗{Color.RESET}")
            print(f"  {Color.WHITE}Interactions:{Color.RESET}     {self.total_interactions}")
            print(f"  {Color.WHITE}New Learnings:{Color.RESET}     {self.session_learn_count}")
            print(f"  {Color.WHITE}Avg Confidence:{Color.RESET}    {avg_conf:.1%}")
            print(f"  {Color.WHITE}Runtime:{Color.RESET}           {runtime:.0f}s")
            print(f"{Color.CYAN}{Color.BOLD}╚════════════════════════╝{Color.RESET}\n")
            return True

        elif lower_text == "/clear":
            self.clear_screen()
            return True

        elif lower_text == "/train":
            self.train_ai()
            return True

        elif lower_text == "/status":
            memory_usage = random.randint(45, 78)
            print(f"\n{Color.CYAN}{Color.BOLD}╔══ System Status ══╗{Color.RESET}")
            print(f"  {Color.WHITE}Memory Usage:{Color.RESET}    {Color.GREEN if memory_usage < 60 else Color.YELLOW}{memory_usage}%{Color.RESET}")
            print(f"  {Color.WHITE}Knowledge Base:{Color.RESET}  {Color.GREEN}OPTIMAL{Color.RESET}")
            print(f"  {Color.WHITE}Neural Network:{Color.RESET}  {Color.GREEN}ACTIVE{Color.RESET}")
            print(f"  {Color.WHITE}NLP Pipeline:{Color.RESET}    {Color.GREEN}OPERATIONAL{Color.RESET}")
            print(f"  {Color.WHITE}Groq Provider:{Color.RESET}   {Color.GREEN if self.provider.enabled else Color.YELLOW}{'ENABLED' if self.provider.enabled else 'SET GROQ_API_KEY'}{Color.RESET}")
            print(f"{Color.CYAN}{Color.BOLD}╚══════════════════╝{Color.RESET}\n")
            return True

        if lower_text.startswith("learn "):
            payload = text[6:]
            if "|" in payload:
                q, a = payload.split("|", 1)
                self.knowledge.learn(q.strip(), a.strip())
                self.session_learn_count += 1
                print(f"\n{Color.GREEN}{Color.BOLD}  ✓ Knowledge Vector Synchronized{Color.RESET}")
                print(f"  {Color.DIM}└─ Pattern mapped to semantic space{Color.RESET}\n")
            else:
                print(f"\n{Color.RED}{Color.BOLD}  ✗ Invalid Format{Color.RESET}")
                print(f"  {Color.DIM}Usage: learn [question] | [answer]{Color.RESET}\n")
            return True

        if lower_text.startswith("remember my "):
            match = re.match(r"remember my (.+?) is (.+)", text, re.IGNORECASE)
            if match:
                key_attr, val_attr = match.group(1).strip(), match.group(2).strip()
                self.memory.remember_profile_fact(self.user, key_attr, val_attr)
                print(f"\n{Color.GREEN}{Color.BOLD}  ✓ Profile Attribute Stored{Color.RESET}")
                print(f"  {Color.DIM}└─ metadata.{key_attr} → '{val_attr}'{Color.RESET}\n")
            else:
                print(f"\n{Color.RED}{Color.BOLD}  ✗ Invalid Format{Color.RESET}")
                print(f"  {Color.DIM}Usage: remember my [property] is [value]{Color.RESET}\n")
            return True

        return False

    def execute_chat_pipeline(self, user_input):
        self.total_interactions += 1
        print(f"{Color.DIM}  Processing...{Color.RESET}\n")

        answer, conf = self.brain.process_pipeline(self.user, user_input)
        self.confidence_scores.append(conf)

        if answer is not None:
            return answer

        print(f"{Color.YELLOW}  ⚠ I don't know that yet.{Color.RESET}")
        print(f"  {Color.DIM}Tip: teach me instantly with: learn {user_input} | [best answer]{Color.RESET}")
        return None

    def run(self):
        self.boot_sequence()
        while True:
            try:
                prompt = f"{Color.CYAN}{Color.BOLD}  ❯{Color.RESET} "
                user_input = input(f"\n{prompt}").strip()
            except (KeyboardInterrupt, EOFError):
                print(f"\n\n{Color.YELLOW}  ⚠ Interrupt detected{Color.RESET}")
                break

            if user_input.lower() in ["exit", "quit", "shutdown"]:
                print(f"\n{Color.CYAN}{Color.BOLD}╔══ Session Summary ══╗{Color.RESET}")
                print(f"  {Color.WHITE}Total Interactions:{Color.RESET} {self.total_interactions}")
                print(f"  {Color.WHITE}New Vectors Mapped:{Color.RESET} {self.session_learn_count}")
                runtime = time.time() - self.start_time
                print(f"  {Color.WHITE}Session Duration:{Color.RESET}  {runtime:.0f}s")
                print(f"{Color.CYAN}{Color.BOLD}╚══════════════════════╝{Color.RESET}")
                print(f"\n{Color.GREEN}{Color.BOLD}  ✓ Systems shutting down cleanly...{Color.RESET}\n")
                break

            if not user_input:
                continue

            if self.handle_system_commands(user_input):
                continue

            final_response = self.execute_chat_pipeline(user_input)
            if final_response:
                print(f"{Color.CYAN}{Color.BOLD}  Bot:{Color.RESET} {final_response}")
                self.memory.add_to_history(user_input, final_response)


if __name__ == "__main__":
    try:
        app = StellightEngine()
        app.run()
    except Exception as e:
        print(f"\n{Color.RED}{Color.BOLD}  ✗ Critical Error: {e}{Color.RESET}\n")
        sys.exit(1)
