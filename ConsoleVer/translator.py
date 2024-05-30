from googletrans import Translator

#print (googletrans.LANGUAGES)  

text = "Dzień dobry"
translatedText = "en"

translator = Translator()

detectedLang = translator.detect(text).lang.lower()
destinationLang = translatedText.lower()


translation = translator.translate(text, src = detectedLang, dest = destinationLang)

print(detectedLang)
print(translation.text)