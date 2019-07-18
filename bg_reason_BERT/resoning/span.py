import numpy as np
import torch


def print_wordpiece_answer(tokenized_text, start, end):
    ans = ''
    sep_index = tokenized_text.index('[SEP]') + 1
    if start >= sep_index:

        for i in range(start, end + 1):
            w = tokenized_text[i]
            if w[0:2] != '##':
                ans += ' '
            else:
                w = w[2:]

            ans += w

    return ans


def predict_span(model, tokenizer, qw, max_len=300, use_gpu=False):
    PAD_ID = tokenizer.convert_tokens_to_ids(['[PAD]'])

    indexed_tokens = []
    segments_ids = []
    tokenized_texts = []

    batch_max_len = 0

    for question, wiki in qw:
        text = "[CLS] " + question + " [SEP] " + wiki
        tokenized_text = tokenizer.tokenize(text)

        # Truncate to max_
        tokenized_text = tokenized_text[:max_len - 2]
        tokenized_text.append("[SEP]")

        # Convert token to vocabulary indices
        it = np.array(tokenizer.convert_tokens_to_ids(tokenized_text))
        # Define sentence A and B indices associated to 1st and 2nd sentences (see paper)
        si = np.ones(len(it), dtype=np.long)
        sep_index = tokenized_text.index('[SEP]') + 1
        si[:sep_index + 1] = 0

        indexed_tokens.append(it)
        segments_ids.append(si)
        tokenized_texts.append(tokenized_text)

        batch_max_len = max(batch_max_len, len(it))

    for i in range(len(segments_ids)):
        it = indexed_tokens[i]
        si = segments_ids[i]
        size = len(it)
        if size < batch_max_len:
            pad = np.zeros(shape=(batch_max_len - size), dtype=np.long)
            indexed_tokens[i] = np.concatenate((it, pad))
            segments_ids[i] = np.concatenate((si, pad))

    indexed_tokens = np.array(indexed_tokens)
    segments_ids = np.array(segments_ids)

    # Convert inputs to PyTorch tensors
    tokens_tensor = torch.tensor(indexed_tokens)
    segments_tensors = torch.tensor(segments_ids)

    # If you have a GPU, put everything on cuda
    if use_gpu:
        tokens_tensor = tokens_tensor.to('cuda')
        segments_tensors = segments_tensors.to('cuda')
        # model.to('cuda')

    # Predict all tokens
    with torch.no_grad():

        start_logits, end_logits = model(tokens_tensor, segments_tensors)

        starts = torch.argmax(start_logits, 1)
        ends = torch.argmax(end_logits, 1)

        res = []
        for j, (start, end) in enumerate(zip(starts, ends)):
            ans = ''
            score = 0.

            start = start.item()
            end = min(end.item(), len(tokenized_texts[j]))  # Ignore pad

            if start >= sep_index:
                for i in range(start, end + 1):
                    w = tokenized_texts[j][i]
                    if w[0:2] != '##':
                        ans += ' '
                    else:
                        w = w[2:]
                    ans += w
                score = (start_logits[j].data[start].item() *
                         end_logits[j].data[end].item())

            res.append((ans.strip(), score))

    return res
