HOST="com.smarter.codes"

mongoexport --host $HOST --db "noisy_NER" --collection "Entity_to_Command" --out Entity_to_Command.json --query '{"how_this_record":"CommandNetTraining"}'


