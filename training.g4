grammar training;

workout: exercise+;

EXERCISE_NAME: 'Deadlift' | 'Squat' | 'Bench press'| 'Overhead press' | NAME;
exercise_name : EXERCISE_NAME;
NAME: ALPHABET+ (WS+ ALPHABET+)*;

weight: INT ('.' INT)? 'k'? ;
INT: DIGIT+;
exercise:
    exercise_name weight NEWLINE
    | exercise_name weight ':'? set_ NEWLINE
    | exercise_name ':'? set_ NEWLINE;

set_:
    single_rep_set (','? set_)*
    | group_of_rep_set (','? set_)*
    | whole_set_ (','? set_)*;

whole_set_: INT 'x' INT 'x' weight;
group_of_rep_set: INT 'x' INT;
single_rep_set: INT;

fragment DIGIT: '0'..'9' ;

ALPHABET: [a-zA-Z] | [áéíóúñ] | [-] ;
NEWLINE:'\r'? '\n' ;
WS:   [ \t]+ -> skip;
