both() {
    ./generic.sh "$1"
    ./generic.sh "$1" --use_8bit
}
# a model with a comment of,
# > TOKENIZER BUG
# Indicates the following errors were printed:
# > The tokenizer class you load from this checkpoint is not the same type as the class this function is called from. It may result in unexpected tokenization.
# > The tokenizer class you load from this checkpoint is 'PreTrainedTokenizerFast'.
# > The class this function is called from is 'GPTNeoXTokenizerFast'.
both EleutherAI/pythia-19m
both EleutherAI/pythia-19m-deduped
both EleutherAI/pythia-125m
both EleutherAI/pythia-125m-deduped # TOKENIZER BUG
both EleutherAI/pythia-350m
both EleutherAI/pythia-350m-deduped
both EleutherAI/pythia-800m
both EleutherAI/pythia-800m-deduped
both EleutherAI/pythia-1.3b
both EleutherAI/pythia-1.3b-deduped # TOKENIZER BUG
both EleutherAI/pythia-2.7b
both EleutherAI/pythia-2.7b-deduped
both EleutherAI/pythia-6.7b
both EleutherAI/pythia-6.7b-deduped # TOKENIZER BUG
./generic.sh EleutherAI/pythia-13b --use_8bit
./generic.sh EleutherAI/pythia-13b-deduped --use_8bit
both 'EleutherAI/gpt-j-6B' 
both 'EleutherAI/gpt-neo-2.7B'
both 'hakurei/litv2-6B-rev3'
./generic.sh 'EleutherAI/gpt-neox-20b' --use_8bit
