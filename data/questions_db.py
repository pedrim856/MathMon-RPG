# MathMon RPG - Questions Database & Procedural Generator
import random
import math as math_module
from settings import CHALLENGE_MATH, CHALLENGE_EQUATION, CHALLENGE_MEMORY, CHALLENGE_LOGIC


class QuestionGenerator:
    """Generates questions for battle challenges."""

    @staticmethod
    def generate(challenge_type, difficulty_level):
        """Generate a question based on type and difficulty.

        Returns dict: {question, answer, options (for multiple choice), timer}
        """
        # Clamp difficulty
        diff = max(1, min(10, difficulty_level))

        if challenge_type == CHALLENGE_MATH:
            return QuestionGenerator._gen_math(diff)
        elif challenge_type == CHALLENGE_EQUATION:
            return QuestionGenerator._gen_equation(diff)
        elif challenge_type == CHALLENGE_MEMORY:
            return QuestionGenerator._gen_memory(diff)
        elif challenge_type == CHALLENGE_LOGIC:
            return QuestionGenerator._gen_logic(diff)
        else:
            return QuestionGenerator._gen_math(diff)

    @staticmethod
    def _gen_math(diff):
        """Generate arithmetic questions."""
        if diff <= 2:
            # Simple addition/subtraction
            a = random.randint(1, 10 * diff)
            b = random.randint(1, 10 * diff)
            op = random.choice(["+", "-"])
            if op == "-" and b > a:
                a, b = b, a
            answer = a + b if op == "+" else a - b
            question = f"{a} {op} {b} = ?"

        elif diff <= 4:
            # Add multiplication
            ops = ["+", "-", "×"]
            op = random.choice(ops)
            if op == "×":
                a = random.randint(2, 5 + diff)
                b = random.randint(2, 5 + diff)
                answer = a * b
            elif op == "+":
                a = random.randint(10, 20 * diff)
                b = random.randint(10, 20 * diff)
                answer = a + b
            else:
                a = random.randint(20, 30 * diff)
                b = random.randint(1, a)
                answer = a - b
            question = f"{a} {op} {b} = ?"

        elif diff <= 6:
            # Include division, larger numbers
            ops = ["+", "-", "×", "÷"]
            op = random.choice(ops)
            if op == "÷":
                b = random.randint(2, 8 + diff)
                answer = random.randint(2, 10 + diff)
                a = b * answer
            elif op == "×":
                a = random.randint(3, 10 + diff)
                b = random.randint(3, 10 + diff)
                answer = a * b
            elif op == "+":
                a = random.randint(20, 50 * diff)
                b = random.randint(20, 50 * diff)
                answer = a + b
            else:
                a = random.randint(50, 100 * diff)
                b = random.randint(1, a)
                answer = a - b
            question = f"{a} {op} {b} = ?"

        elif diff <= 8:
            # Multi-step, larger numbers
            choice = random.randint(0, 2)
            if choice == 0:
                a = random.randint(10, 30)
                b = random.randint(2, 10)
                c = random.randint(1, 20)
                answer = a * b + c
                question = f"{a} × {b} + {c} = ?"
            elif choice == 1:
                a = random.randint(10, 50)
                b = random.randint(2, 12)
                c = random.randint(1, 15)
                answer = a + b * c
                question = f"{a} + {b} × {c} = ?"
            else:
                b = random.randint(2, 12)
                answer = random.randint(5, 30)
                a = b * answer
                c = random.randint(1, 20)
                final = answer + c
                question = f"{a} ÷ {b} + {c} = ?"
                answer = final

        else:
            # Hard multi-step
            choice = random.randint(0, 2)
            if choice == 0:
                a = random.randint(10, 50)
                b = random.randint(10, 50)
                c = random.randint(2, 10)
                answer = (a + b) * c
                question = f"({a} + {b}) × {c} = ?"
            elif choice == 1:
                a = random.randint(5, 20)
                answer = a * a
                question = f"{a}² = ?"
            else:
                a = random.randint(15, 99)
                b = random.randint(15, 99)
                c = random.randint(2, 8)
                answer = a * b
                question = f"{a} × {b} = ?"

        # Generate wrong options
        options = QuestionGenerator._gen_options(answer, diff)
        timer = max(5, 16 - diff)

        return {
            "question": question,
            "answer": str(answer),
            "timer": timer,
            "type": "input",  # input = type answer
        }

    @staticmethod
    def _gen_equation(diff):
        """Generate equation-solving questions (find x)."""
        if diff <= 3:
            # x + a = b
            x = random.randint(1, 10 * diff)
            a = random.randint(1, 10 * diff)
            b = x + a
            op = random.choice(["+", "-"])
            if op == "+":
                question = f"x + {a} = {b}"
                answer = x
            else:
                question = f"x - {a} = {x - a}" if x > a else f"{b} - x = {a}"
                answer = x if x > a else x

        elif diff <= 5:
            # a*x + b = c  or  a*x = c
            x = random.randint(1, 8 + diff)
            a = random.randint(2, 5 + diff // 2)
            b = random.randint(0, 10)
            c = a * x + b
            if b == 0:
                question = f"{a}x = {c}"
            else:
                question = f"{a}x + {b} = {c}"
            answer = x

        elif diff <= 7:
            # a*x + b = c with bigger numbers
            x = random.randint(2, 15)
            a = random.randint(2, 8)
            b = random.randint(1, 20)
            c = a * x + b
            question = f"{a}x + {b} = {c}"
            answer = x

        else:
            # More complex: a*x + b = c*x + d
            x = random.randint(1, 12)
            a = random.randint(3, 10)
            b = random.randint(1, 20)
            c = random.randint(1, a - 1)
            d = (a - c) * x + b
            question = f"{a}x + {b} = {c}x + {d}"
            answer = x

        question = f"Encontre x: {question}"
        options = QuestionGenerator._gen_options(answer, diff)
        timer = max(6, 18 - diff)

        return {
            "question": question,
            "answer": str(answer),
            "timer": timer,
            "type": "input",
        }

    @staticmethod
    def _gen_memory(diff):
        """Generate memory sequence challenge."""
        # Length of sequence based on difficulty
        length = min(3 + diff // 2, 9)

        # Color/number sequence
        if diff <= 4:
            # Number sequence
            sequence = [random.randint(1, 9) for _ in range(length)]
            return {
                "question": "Memorize a sequência de números!",
                "sequence": sequence,
                "answer": sequence,
                "timer": max(3, 8 - diff // 2),  # Display time
                "input_timer": max(8, 15 - diff),  # Input time
                "type": "memory_numbers",
            }
        else:
            # Color sequence
            colors = ["V", "Az", "Am", "Vd", "Lj", "Rx"]  # Vermelho, Azul, Amarelo, Verde, Laranja, Roxo
            color_names = {
                "V": "Vermelho", "Az": "Azul", "Am": "Amarelo",
                "Vd": "Verde", "Lj": "Laranja", "Rx": "Roxo"
            }
            max_colors = min(len(colors), 3 + diff // 2)
            available = colors[:max_colors]
            sequence = [random.choice(available) for _ in range(length)]
            return {
                "question": "Memorize a sequência de cores!",
                "sequence": sequence,
                "color_names": color_names,
                "answer": sequence,
                "timer": max(3, 8 - diff // 2),
                "input_timer": max(8, 18 - diff),
                "type": "memory_colors",
            }

    @staticmethod
    def _gen_logic(diff):
        """Generate logic/pattern questions."""
        if diff <= 3:
            # Simple arithmetic sequence
            start = random.randint(1, 10)
            step = random.randint(1, 5)
            seq = [start + step * i for i in range(5)]
            answer = seq[-1]
            display = seq[:-1]
            question = f"Qual o próximo? {', '.join(map(str, display))}, ?"

        elif diff <= 5:
            # Geometric or complex arithmetic
            choice = random.randint(0, 2)
            if choice == 0:
                # Double each time
                start = random.randint(1, 5)
                seq = [start * (2 ** i) for i in range(5)]
                answer = seq[-1]
                display = seq[:-1]
                question = f"Qual o próximo? {', '.join(map(str, display))}, ?"
            elif choice == 1:
                # Add increasing amounts
                start = random.randint(1, 5)
                seq = [start]
                for i in range(1, 5):
                    seq.append(seq[-1] + i + 1)
                answer = seq[-1]
                display = seq[:-1]
                question = f"Qual o próximo? {', '.join(map(str, display))}, ?"
            else:
                # Square numbers
                start = random.randint(1, 4)
                seq = [(start + i) ** 2 for i in range(5)]
                answer = seq[-1]
                display = seq[:-1]
                question = f"Qual o próximo? {', '.join(map(str, display))}, ?"

        elif diff <= 7:
            choice = random.randint(0, 2)
            if choice == 0:
                # Fibonacci-like
                a, b = random.randint(1, 5), random.randint(1, 5)
                seq = [a, b]
                for _ in range(4):
                    seq.append(seq[-1] + seq[-2])
                answer = seq[-1]
                display = seq[:-1]
                question = f"Qual o próximo? {', '.join(map(str, display))}, ?"
            elif choice == 1:
                # Multiply then add
                start = random.randint(1, 3)
                mult = random.randint(2, 3)
                add = random.randint(1, 3)
                seq = [start]
                for _ in range(4):
                    seq.append(seq[-1] * mult + add)
                answer = seq[-1]
                display = seq[:-1]
                question = f"Qual o próximo? {', '.join(map(str, display))}, ?"
            else:
                # Alternating operations
                start = random.randint(2, 6)
                seq = [start]
                for i in range(4):
                    if i % 2 == 0:
                        seq.append(seq[-1] * 2)
                    else:
                        seq.append(seq[-1] + 3)
                answer = seq[-1]
                display = seq[:-1]
                question = f"Qual o próximo? {', '.join(map(str, display))}, ?"
        else:
            choice = random.randint(0, 1)
            if choice == 0:
                # Triangular numbers or similar
                seq = [n * (n + 1) // 2 for n in range(1, 7)]
                answer = seq[-1]
                display = seq[:-1]
                question = f"Qual o próximo? {', '.join(map(str, display))}, ?"
            else:
                # Powers
                base = random.randint(2, 3)
                seq = [base ** i for i in range(1, 6)]
                answer = seq[-1]
                display = seq[:-1]
                question = f"Qual o próximo? {', '.join(map(str, display))}, ?"

        options = QuestionGenerator._gen_options(answer, diff)
        timer = max(6, 16 - diff)

        return {
            "question": question,
            "answer": str(answer),
            "timer": timer,
            "type": "input",
        }

    @staticmethod
    def _gen_options(correct_answer, diff):
        """Generate multiple choice options including the correct answer."""
        answer = int(correct_answer) if isinstance(correct_answer, (int, float)) else int(correct_answer)
        options = {answer}

        # Generate plausible wrong answers
        attempts = 0
        while len(options) < 4 and attempts < 50:
            attempts += 1
            offset_range = max(3, abs(answer) // 3 + diff)
            wrong = answer + random.randint(-offset_range, offset_range)
            if wrong != answer and wrong >= 0:
                options.add(wrong)

        # Ensure we have 4 options
        while len(options) < 4:
            options.add(answer + len(options) * 2 + 1)

        options = list(options)
        random.shuffle(options)
        return [str(o) for o in options]
