import numpy as np
import torch


def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()


def transform_single_example(tokenizer, wiki, question, options, max_len=320):
    text = "[CLS] " + wiki + " [SEP] " + question

    indexed_tokens_arr = []
    segments_ids_arr = []
    input_mask_arr = []

    max_tokens = 0

    for opt in options:
        text_opt = ' '.join((text, opt))
        tokenized_text = tokenizer.tokenize(text_opt)

        # Truncate to max_
        tokenized_text = tokenized_text[:max_len - 2]
        tokenized_text.append("[SEP]")

        # Convert token to vocabulary indices
        indexed_tokens = tokenizer.convert_tokens_to_ids(tokenized_text)
        # Define sentence A and B indices associated to 1st and 2nd sentences (see paper)
        segments_ids = np.ones(len(indexed_tokens), dtype=np.long)
        sep_index = tokenized_text.index('[SEP]') + 1
        segments_ids[:sep_index + 1] = 0

        indexed_tokens_arr.append(indexed_tokens)
        segments_ids_arr.append(segments_ids)
        input_mask_arr.append(np.ones((len(indexed_tokens)), dtype=np.long))

        max_tokens = max(max_tokens, len(indexed_tokens))

    for i in range(len(segments_ids_arr)):
        it = indexed_tokens_arr[i]
        si = segments_ids_arr[i]
        im = input_mask_arr[i]

        size = len(it)
        if size < max_tokens:
            pad = np.zeros(shape=((max_tokens - size)), dtype=np.long)
            indexed_tokens_arr[i] = np.concatenate((it, pad))
            segments_ids_arr[i] = np.concatenate((si, pad))
            input_mask_arr[i] = np.concatenate((im, pad))

    # Convert inputs to PyTorch tensors
    tokens_tensor = torch.tensor([indexed_tokens_arr])
    segments_tensors = torch.tensor([segments_ids_arr])
    input_masks_tensor = torch.tensor([input_mask_arr])

    return tokens_tensor, segments_tensors, input_masks_tensor


def predict(model, tokenizer, wiki, question, options, max_len=320, use_gpu=False):
    tokens_tensor, segments_tensors, input_masks_tensor = \
        transform_single_example(tokenizer, wiki, question, options, max_len)

    # If you have a GPU, put everything on cuda
    if use_gpu:
        tokens_tensor = tokens_tensor.to('cuda')
        segments_tensors = segments_tensors.to('cuda')
        input_masks_tensor = input_masks_tensor.to('cuda')

    with torch.no_grad():
        logits = model(tokens_tensor, segments_tensors, input_masks_tensor)

        return np.array(logits.tolist())
