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
from memory import MemoryManager
from learn import KnowledgeEngine
from brain import DecisionBrain

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
        self.session_learn_count = 0
        self.total_interactions = 0
        self.confidence_scores = []
        self.term_width = os.get_terminal_size().columns if hasattr(os, 'get_terminal_size') else 80

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_centered(self, text, color=Color.WHITE, style=""):
        clean_text = re.sub(r'\033\[[0-9;]*m', '', text)
        padding = max(0, (self.term_width - len(clean_text)) // 2)
        print(f"{' ' * padding}{style}{color}{text}{Color.RESET}")

    def get_system_info(self):
        """Gather real system data. Returns a list of lines for the panel."""
        def safe(func, default="[REDACTED]"):
            try: return func()
            except: return default

        user = self.user
        host = safe(lambda: socket.gethostname(), "localhost")
        os_name = f"{platform.system()} {platform.release()}" if platform.system() else "Unknown"
        kernel = platform.version() or "[REDACTED]"
        cpu = platform.processor() or "[REDACTED]"
        mem = "[REDACTED]"
        if os.path.exists('/proc/meminfo'):
            try:
                with open('/proc/meminfo') as f:
                    for line in f:
                        if line.startswith('MemTotal:'):
                            mem_kb = int(line.split()[1])
                            mem = f"{mem_kb / 1024 / 1024:.1f} GiB"
                            break
            except:
                pass
        python_ver = platform.python_version()
        session_id = hex(hash(user + str(self.start_time)))[2:10] if hasattr(self,'start_time') else hex(hash(user))[2:10]
        started = time.strftime('%Y-%m-%d %H:%M:%S') if hasattr(self,'start_time') else "just now"

        info = [
            f"  User: {user}",
            f"  Hostname: {host}",
            f"  OS: {os_name}",
            f"  Kernel: {kernel}",
            f"  CPU: {cpu}",
            f"  RAM: {mem}",
            f"  Python: {python_ver}",
            f"  Session ID: 0x{session_id}",
            f"  Started: {started}"
        ]
        return info

    def boot_sequence(self):
        self.clear_screen()

        # Header
        print(f"\n{Color.CYAN}{Color.BOLD}")
        self.print_centered("╔══════════════════════════════════════════════════════════╗", Color.CYAN, Color.BOLD)
        self.print_centered("║           STELLIGHT AI PROTOTYPE v0.1                   ║", Color.CYAN, Color.BOLD)
        self.print_centered("║      Advanced Neural Language Processing Engine          ║", Color.CYAN, Color.BOLD)
        self.print_centered("╚══════════════════════════════════════════════════════════╝", Color.CYAN, Color.BOLD)
        print(f"{Color.RESET}\n")
        time.sleep(0.4)

        print(f"{Color.DIM}{'─' * self.term_width}{Color.RESET}")
        print(f"{Color.BOLD}{Color.WHITE}  SYSTEM INITIALIZATION{Color.RESET}")
        print(f"{Color.DIM}{'─' * self.term_width}{Color.RESET}\n")

        boot_tasks = [
            ("Neural Core Initialization", "CPU: 3.2GHz | RAM: 16GB"),
            ("Memory Subsystem Loading", "Vectors: 1.2M | Clusters: 847"),
            ("NLP Pipeline Activation", "Tokenizer: BPE | Embeddings: 768d"),
            ("Semantic Analysis Matrix", "Accuracy: 94.7% | Recall: 91.2%"),
            ("Lexical Normalization Filters", "Languages: EN, ES, FR, DE"),
            ("Mathematical Logic Coprocessor", "Precision: FP32 | Throughput: 1.2T OPS"),
            ("Knowledge Graph Integration", "Nodes: 45K | Edges: 128K"),
            ("Session Handshake Protocol", "TLS 1.3 | Latency: 12ms"),
        ]

        bar_width = 30
        for i, (task, specs) in enumerate(boot_tasks):
            # Draw empty bar
            sys.stdout.write(f"  {Color.CYAN}[{Color.DIM}{'░'*bar_width}{Color.CYAN}] {Color.WHITE}{task:.<40} ")
            sys.stdout.flush()

            # Animate bar filling
            for filled in range(1, bar_width + 1):
                time.sleep(0.02)  # speed of fill
                bar = f"{Color.GREEN}{'█'*filled}{Color.DIM}{'░'*(bar_width-filled)}{Color.RESET}"
                sys.stdout.write(f"\r  {Color.CYAN}[{bar}] {Color.WHITE}{task:.<40} {Color.YELLOW}⣿{Color.RESET}")
                sys.stdout.flush()

            # Completed bar
            bar_full = f"{Color.GREEN}{'█'*bar_width}{Color.RESET}"
            sys.stdout.write(f"\r  {Color.CYAN}[{bar_full}] {Color.WHITE}{task:.<40} {Color.GREEN}{Color.BOLD}✓ ONLINE{Color.RESET}")
            print(f"\n  {Color.DIM}     └─ {specs}{Color.RESET}\n")
            time.sleep(0.1)

        # Separator and system info panel
        print(f"\n{Color.DIM}{'─' * self.term_width}{Color.RESET}")

        info = self.get_system_info()
        max_len = max(len(line) for line in info)
        box_width = max_len + 4
        horizontal = '─' * (box_width - 2)

        print(f"  {Color.MAGENTA}┌{horizontal}┐{Color.RESET}")
        for line in info:
            print(f"  {Color.MAGENTA}│{Color.RESET} {line}{' ' * (max_len - len(line))} {Color.MAGENTA}│{Color.RESET}")
        print(f"  {Color.MAGENTA}└{horizontal}┘{Color.RESET}")

        print(f"\n{Color.CYAN}{Color.BOLD}  ✦ Welcome back, {self.user}{Color.RESET}")
        print(f"  {Color.DIM}All systems nominal. Ready for input.{Color.RESET}")
        print(f"\n{Color.DIM}{'─' * self.term_width}{Color.RESET}\n")

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

        elif lower_text == "/status":
            memory_usage = random.randint(45, 78)
            print(f"\n{Color.CYAN}{Color.BOLD}╔══ System Status ══╗{Color.RESET}")
            print(f"  {Color.WHITE}Memory Usage:{Color.RESET}    {Color.GREEN if memory_usage < 60 else Color.YELLOW}{memory_usage}%{Color.RESET}")
            print(f"  {Color.WHITE}Knowledge Base:{Color.RESET}  {Color.GREEN}OPTIMAL{Color.RESET}")
            print(f"  {Color.WHITE}Neural Network:{Color.RESET}  {Color.GREEN}ACTIVE{Color.RESET}")
            print(f"  {Color.WHITE}NLP Pipeline:{Color.RESET}    {Color.GREEN}OPERATIONAL{Color.RESET}")
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

        if answer is not None and conf >= self.brain.HIGH_CONF:
            return answer

        if answer is not None and conf >= self.brain.LOW_CONF:
            print(f"{Color.CYAN}{Color.BOLD}  Bot:{Color.RESET} {answer}")
            print(f"{Color.YELLOW}  (Confidence: {conf:.0%}){Color.RESET}")
            verify = input(f"{Color.BOLD}  Was that right? (yes/no): {Color.RESET}").lower().strip()
            if verify in ['yes','y']:
                self.knowledge.learn(user_input, answer)
                return answer
            else:
                correction = input(f"{Color.BOLD}  What should I say instead? {Color.RESET}").strip()
                if correction:
                    self.knowledge.learn(user_input, correction)
                    self.session_learn_count += 1
                    return correction
                return None

        print(f"{Color.YELLOW}  ⚠ I don't know that yet.{Color.RESET}")
        teach = input(f"{Color.BOLD}  Teach me: {Color.RESET}").strip()
        if teach:
            self.knowledge.learn(user_input, teach)
            self.session_learn_count += 1
            return teach
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
