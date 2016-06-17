#!/bin/bash

BASE_PATH="/home/cop15rj/lexsub"
PARSER_BASE="$BASE_PATH/stanford-parser-full-2015-12-09"
PARSER_CLASS="edu.stanford.nlp.parser.nndep.DependencyParser"
INPUT_FILE="$1" # "/data/cop15rj/corpus/text8"
MODEL_FILE="$PARSER_BASE/edu/stanford/nlp/models/parser/nndep/PTB_CoNLL_params.txt.gz"
TAGGER_MODEL_FILE="$BASE_PATH/stanford-postagger-2015-12-09/models/english-left3words-distsim.tagger"
OUTPUT_FILE="$2" # "$BASE_PATH/dep_text8_1.txt"

module load apps/java/1.8u71

cd $BASE_PATH/stanford-parser-full-2015-12-09

java -Xmx7g -cp "$PARSER_BASE/*:" $PARSER_CLASS -textFile $INPUT_FILE -model $MODEL_FILE -tagger.model $TAGGER_MODEL_FILE -outFile $OUTPUT_FILE

