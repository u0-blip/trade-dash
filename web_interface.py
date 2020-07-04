from tv_script import helper
from tv_script.helper import RNN


rnn = None
int_text, vocab_to_int, int_to_vocab, token_dict = helper.load_preprocess()
gen_length = 400

def get_script(name):
    global rnn
    if rnn == None:
        rnn = helper.load_model('trained_rnn_og')

    pad_word = helper.SPECIAL_WORDS['PADDING']
    generated_script = helper.generate(rnn, vocab_to_int[name], int_to_vocab, token_dict, vocab_to_int[pad_word], gen_length)
    return generated_script
