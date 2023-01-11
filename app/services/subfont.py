from fontTools import subset

def make_subfont(font_path, output_path, text):
    subsetter = subset.Subsetter()
    subsetter.populate(text=text)
    font = subset.load_font(font_path, subset.Options())
    subsetter.subset(font)
    font.save(output_path)
