import re


class SentenceGenerator:

    def __init__(self):
        self.words = []

    def add_word(self, word):
        """
        Add a recognized sign to the sentence.
        """

        if not word:
            return

        word = word.strip().lower()

        if not word:
            return

        # Avoid adding the same word repeatedly
        # because webcam predictions happen every frame.
        if self.words and self.words[-1] == word:
            return

        self.words.append(word)

    def remove_last_word(self):
        """
        Remove the most recently added word.
        """

        if self.words:
            self.words.pop()

    def clear(self):
        """
        Clear the current sentence.
        """

        self.words.clear()

    def get_words(self):
        return self.words.copy()

    def get_raw_sentence(self):
        """
        Return the recognized words.
        """

        return " ".join(self.words)

    def generate_sentence(self):
        """
        Convert recognized words into a readable sentence.
        """

        if not self.words:
            return ""

        sentence = " ".join(self.words)

        # ----------------------------------
        # Simple phrase corrections
        # ----------------------------------

        replacements = {
            "i am happy": "I am happy.",
            "i am sorry": "I am sorry.",
            "hello you": "Hello.",
            "you happy": "You are happy.",
            "you good": "You are good.",
            "good home": "Good home.",
            "eat home": "Eat at home.",
            "you eat": "You eat.",
            "hello goodbye": "Hello and goodbye."
        }

        sentence_lower = sentence.lower()

        if sentence_lower in replacements:
            return replacements[sentence_lower]

        # ----------------------------------
        # Capitalize first letter
        # ----------------------------------

        sentence = sentence.capitalize()

        # ----------------------------------
        # Add punctuation
        # ----------------------------------

        if sentence[-1] not in ".!?":
            sentence += "."

        return sentence


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    generator = SentenceGenerator()

    generator.add_word("hello")
    generator.add_word("i am")
    generator.add_word("happy")

    print("Recognized words:")
    print(generator.get_words())

    print()

    print("Generated sentence:")
    print(generator.generate_sentence())