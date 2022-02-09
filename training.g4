grammar training;

sessions: session+;

EXERCISE_NAME: 'Deadlift' | 'Squat' | 'Bench press'| 'Overhead press' | NAME;
exercise_name : EXERCISE_NAME;
NAME: ALPHABET+ (WS+ ALPHABET+)*;

reps: INT 'k' ;
INT: DIGIT+;
session:
    exercise_name reps NEWLINE
    | exercise_name reps ':'? mini_reps NEWLINE
    | exercise_name ':'? mini_reps NEWLINE;



mini_reps:
    INT (',' mini_reps)*
    | INT 'x' INT mini_reps*
    | INT 'x' INT 'x' INT 'k' mini_reps*;

fragment DIGIT: '0'..'9' ;

ALPHABET: [a-zA-Z] ;
NEWLINE:'\r'? '\n' ;
WS:   [ \t]+ -> skip;
