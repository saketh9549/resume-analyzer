import re

class ReadabilityEngine:
    @staticmethod
    def calculate_flesch_reading_ease(text: str) -> float:
        """
        Locally approximates Flesch Reading Ease score for text.
        Formula: 206.835 - 1.015 * (total_words / total_sentences) - 84.6 * (total_syllables / total_words)
        """
        if not text or not text.strip():
            return 0.0

        # Clean text
        clean_text = re.sub(r'\s+', ' ', text).strip()
        
        words = clean_text.split()
        total_words = len(words)
        if total_words == 0:
            return 0.0

        # Sentence count estimation (by dots, question marks, and exclamation marks)
        sentences = re.split(r'[.!?]+', clean_text)
        total_sentences = len([s for s in sentences if s.strip()])
        if total_sentences == 0:
            total_sentences = 1

        # Syllable count estimation
        total_syllables = 0
        vowels = "aeiouy"
        for word in words:
            word = word.lower().strip(".:;!?()\"'-")
            if not word:
                continue
            count = 0
            if word[0] in vowels:
                count += 1
            for index in range(1, len(word)):
                if word[index] in vowels and word[index - 1] not in vowels:
                    count += 1
            if word.endswith("e"):
                count -= 1
            if count == 0:
                count = 1
            total_syllables += count

        asl = total_words / total_sentences
        asw = total_syllables / total_words
        
        score = 206.835 - 1.015 * asl - 84.6 * asw
        # Clamp score between 0 and 100
        return max(0.0, min(100.0, score))

    @classmethod
    def get_readability_metrics(cls, text: str) -> dict:
        """
        Retrieves multiple text density and reading index scores.
        """
        reading_ease = cls.calculate_flesch_reading_ease(text)
        
        # Determine verbal description of readability
        if reading_ease >= 90:
            grade = "Very Easy (5th grade level)"
        elif reading_ease >= 80:
            grade = "Easy (6th grade level)"
        elif reading_ease >= 70:
            grade = "Fairly Easy (7th grade level)"
        elif reading_ease >= 60:
            grade = "Standard (8th-9th grade level)"
        elif reading_ease >= 50:
            grade = "Fairly Difficult (High school level)"
        elif reading_ease >= 30:
            grade = "Difficult (College level)"
        else:
            grade = "Very Confusing (Graduate level)"

        return {
            "flesch_reading_ease_score": round(reading_ease, 1),
            "readability_difficulty_level": grade,
            "word_count": len(text.split()),
            "character_count": len(text)
        }
