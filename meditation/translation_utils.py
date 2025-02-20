from googletrans import Translator

translator = Translator()

def translate_text(text, src_lang, dest_lang):
    """Перекладає текст з мови src_lang до dest_lang."""
    if not text:
        return ''
    result = translator.translate(text, src=src_lang, dest=dest_lang)
    return result.text


def auto_translate_instance(instance, fields, src_lang='uk'):
    """Автоматично перекладає зазначені поля для екземпляра моделі.

    Для кожного поля з fields перевіряється, якщо переклад для мов 'en' та 'fr' відсутній, виконується переклад."""
    for lang in ['en', 'fr']:
        for field in fields:
            translated_field = f"{field}_{lang}"
            current_value = getattr(instance, translated_field, None)
            if not current_value:
                default_value = getattr(instance, field, '')
                if default_value:
                    translated_value = translate_text(default_value, src_lang, lang)
                    setattr(instance, translated_field, translated_value)
    instance.save() 