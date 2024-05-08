from googletrans import Translator

#print (googletrans.LANGUAGES)  

text = "Jag ater god"
translatedText = "EN"

translator = Translator()

detectedLang = translator.detect(text).lang.lower()
destinationLang = translatedText.lower()


translation = translator.translate(text, src = detectedLang, dest = destinationLang)

print(translation.text)