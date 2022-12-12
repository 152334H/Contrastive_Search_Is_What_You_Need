both() {
    ./generic.sh "$1"
    ./generic.sh "$1" --use_8bit
}
both 'EleutherAI/gpt-j-6B' 
both 'EleutherAI/gpt-neo-2.7B'
both 'hakurei/litv2-6B-rev3'
./generic.sh 'EleutherAI/gpt-neox-20b' --use_8bit
