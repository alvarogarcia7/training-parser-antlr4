grammar training;

workout: exercise+;

EXERCISE_NAME: 'Deadlift' | 'Squat' | 'Bench press'| 'Overhead press' | NAME;
exercise_name : EXERCISE_NAME;
NAME: ALPHABET+ (WS+ ALPHABET+)*;

weight: INT ('.' INT)? 'k'? ;
INT: DIGIT+;
exercise: exercise_name ':'? set_ NEWLINE*;

set_:
    set_ ','? set_ #multiple_set_
    | INT #single_rep_set_
    | group_of_rep_set #group_of_rep_set_
    | whole_set_ #whole_set__
    | weight ':'? set_? #weight_
    | INT 'xx' weight (',' weight)* #fixed_reps_multiple_weight
    ;

whole_set_: INT 'x' INT 'x' weight;
group_of_rep_set: INT 'x' INT;

fragment DIGIT: '0'..'9' ;

ALPHABET: [a-zA-Z] | [áéíóúñ] | [-] ;
NEWLINE:'\r'? '\n' ;
WS:   [ \t]+ -> skip;
