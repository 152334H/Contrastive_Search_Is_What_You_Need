import sys
import torch
import argparse
import progressbar

def parse_config():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test_path", type=str)
    parser.add_argument("--max_len", type=int)
    parser.add_argument("--language_code", type=str)
    parser.add_argument("--model_name", type=str)
    parser.add_argument("--save_path_prefix", type=str)
    parser.add_argument("--use_8bit", action='store_true')
    return parser.parse_args()

def parse_text(text, tokenizer, max_len, bos_token_id=None):
    tokens = tokenizer.tokenize(text)
    token_ids = tokenizer.convert_tokens_to_ids(tokens)
    if bos_token_id == None:
        pass
    else:
        token_ids = [bos_token_id] + token_ids
    token_ids = token_ids[:max_len]
    input_ids = torch.LongTensor(token_ids).view(1,-1)
    return input_ids

def is_hf_model(model_name):
    STUBS = ['gpt-neox', 'gpt-neo', 'gpt-j']
    for s in STUBS:
        if s in model_name.lower(): return s
    if 'pythia' in model_name: return 'gpt-neox'
    if 'litv2' in model_name: return 'gpt-j'
    return None

def compute_one_instance_result(model, input_ids, model_name):
    # input_ids : 1 x seqlen
    if is_hf_model(model_name):
        outputs = model(input_ids=input_ids, output_hidden_states=True)
    else:
        outputs = model.model(input_ids=input_ids, output_hidden_states=True)
    last_hidden_states = outputs.hidden_states[-1] # 1 x seqlen x embed_dim

    # compute the sum of cosine similarity and the number of tokens
    bsz, seqlen = input_ids.size()
    norm_rep = last_hidden_states / last_hidden_states.norm(dim=2, keepdim=True)
    cosine_scores = torch.matmul(norm_rep, norm_rep.transpose(1,2)) 
    assert cosine_scores.size() == torch.Size([bsz, seqlen, seqlen])
    cosine_sum_scores = torch.sum(cosine_scores) - seqlen # remove the diagonal cosine scores
    token_num = seqlen * (seqlen - 1)
    return cosine_sum_scores.detach().cpu().item(), token_num

if __name__ == '__main__':
    args = parse_config()
    cuda_available = torch.cuda.is_available()
    device = torch.device('cuda')

    import os
    save_path_prefix = args.save_path_prefix + r'/{}/'.format(args.language_code)
    if os.path.exists(save_path_prefix):
        pass
    else: # recursively construct directory
        os.makedirs(save_path_prefix, exist_ok=True)
    save_name = r'{}{}_isotropy_result.json'.format(args.model_name.split('/')[-1], "_int8" if args.use_8bit else "")
    save_path = save_path_prefix + save_name
    print ('Save path is {}'.format(save_path))

    def load_hf(model_name, model_type, use_8bit=False):
        from transformers import GPT2Tokenizer, GPTNeoXTokenizerFast, AutoTokenizer, GPTJForCausalLM, GPTNeoForCausalLM, GPTNeoXForCausalLM, XGLMForCausalLM, GPT2Tokenizer
        print(f'Evaluating {model_name}')
        modeler = {
            'gpt-neo': GPTNeoForCausalLM,
            'gpt-neox': GPTNeoXForCausalLM,
            'gpt-j': GPTJForCausalLM,
        }[model_type]
        tokenizerer = {
            'gpt-neo': GPT2Tokenizer,
            'gpt-neox': GPTNeoXTokenizerFast,
            'gpt-j': AutoTokenizer,
        }[model_type]
        kwargs = {
            "EleutherAI/gpt-j-6B": {"revision": "float16"}
        }.get(model_name, {})
        model = modeler.from_pretrained(model_name, device_map='auto', load_in_8bit=use_8bit, **kwargs)
        tokenizer = tokenizerer.from_pretrained(model_name)

        return model, tokenizer, None
    print ('Loading model...')
    model_name = args.model_name
    if 'opt' in model_name: # OPT model
        print ('Evaluating OPT model.')
        from simctg.simctgopt import SimCTGOPT
        model = SimCTGOPT(model_name)
        tokenizer = model.tokenizer
        bos_token_id = tokenizer.bos_token_id
    elif model_type := is_hf_model(model_name):
        model, tokenizer, bos_token_id = load_hf(model_name, model_type, args.use_8bit)
    else: # GPT model
        print ('Evaluating GPT model.')
        from simctg.simctggpt import SimCTGGPT
        model = SimCTGGPT(model_name)
        tokenizer = model.tokenizer
        bos_token_id = None
    model.eval()
    if cuda_available and "cuda" not in str(next(model.parameters()).device):
        model = model.cuda(device)
    print ('Model loaded!')

    print ('Loading data...')
    import json
    with open(args.test_path) as f:
        text_dict = json.load(f)
        text_list = text_dict[args.language_code]

    tmp_text_list = [text.strip('\n').strip() for text in text_list]
    text_list = []
    for item in tmp_text_list:
        if len(item) < 2:
            continue
        else:
            text_list.append(item)
    text_list = text_list[:2000]
    print ('Data loaded!')

    print ('Performing inference...')
    data_num = len(text_list)
    p = progressbar.ProgressBar(data_num)
    p.start()
    cosine_score_sum, token_sum = 0., 0.
    with torch.no_grad():
        for index in range(data_num):
            p.update(index)
            text = text_list[index]
            input_ids = parse_text(text, tokenizer, args.max_len, bos_token_id=bos_token_id)
            if cuda_available:
                input_ids = input_ids.cuda(device)
            one_cosine_score_sum, one_token_sum = compute_one_instance_result(model, input_ids, model_name)
            cosine_score_sum += one_cosine_score_sum
            token_sum += one_token_sum
    p.finish()
    print ('Inference completed!')

    averaged_self_similarity = cosine_score_sum / token_sum
    model_isotropy = 1.0 - averaged_self_similarity
    #model_isotropy = round(model_isotropy, 2)

    result_dict = {
        'language_code': args.language_code,
        'model_name': args.model_name,
        'use_8bit': args.use_8bit,
        'isotropy': model_isotropy
    }
    print (r"Language Code:{}, Model:{}, Isotropy:{}".format(args.language_code,
        args.model_name, model_isotropy))

    with open(save_path, 'w') as outfile:
        json.dump([result_dict], outfile, indent=4)
