source ./config 

python ./inference/inference-score.py \
      --model_dir /home/gezi/temp/textsum/model.seq2seq.attention/ \
      --seg_method $online_seg_method \
      --feed_single $feed_single 
