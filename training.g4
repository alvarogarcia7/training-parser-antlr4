grammar training;

// Lexer tokens must be defined before use
// Token ordering is load-bearing: shorter tokens must come after longer ones
// and operator tokens must come before NAME so they match with higher priority
fragment DIGIT: '0'..'9' ;
INT: DIGIT+;
DOTDOT : '..' ;  // must precede DOT
DOT    : '.'  ;
XX     : 'xx' ;  // must precede X
X      : 'x'  ;
COMMA  : ','  ;
SLASH  : '/'  ;
DASH   : '-'  ;  // must precede NAME for '-4' to tokenize as DASH INT
K_UNIT : 'k'  ;  // must precede NAME so 'k' in weights is matched as token
fragment ALPHABET: [a-zA-Z] | [áéíóúñ] ;
HYPHENATED_NAME: ALPHABET* '-' ALPHABET+ ;
NAME: [a-zA-Záéíóúñ] ALPHABET* (WS+ ALPHABET+)* ;
NEWLINE: '\r'? '\n' ;
WS:     [ \t]+ -> skip ;
// Lines starting with '#' are comments and must not be parsed (TP-16).
// The column==0 predicate anchors this to the line start so a mid-line '#'
// (e.g. inside '@#$') is left untouched and still raised as an error.
// Consume the trailing newline too so a whole comment line disappears entirely
// rather than leaving a stray NEWLINE token that breaks 'workout: exercise+'.
COMMENT: {self.column == 0}? '#' ~[\r\n]* ('\r'? '\n')? -> skip ;

// Parser rules
workout: exercise+;

exercise_name: HYPHENATED_NAME | NAME;

// Two weight variants. weight_dot is v1-compatible (dot decimals).
// weight_com allows comma-decimals; used inside /-delimited contexts and for standalone
// comma-decimal weights (e.g. '62,5').
// Note: weight_com must be tried before weight_dot to prefer comma-decimals in slash-delimited contexts
weight_com : INT (COMMA INT)? K_UNIT? ;
weight_dot : INT (DOT INT)? K_UNIT? ;
weight     : weight_com | weight_dot ;

exercise: exercise_name ':'? set_ NEWLINE*;

sep        : X | DOT ;
double_sep : XX | DOTDOT ;
rir_dash   : DASH? INT ;

// A single weight inside a fixed-reps multi-weight list, optionally carrying
// its own RIR (e.g. '65-4'). Lets each weight in '10..50-4,65-4,65-3' hold a
// distinct RIR while keeping the shared fixed-rep count from the '10..' prefix.
fixed_rep_weight : weight_dot rir_dash? ;

set_:
  // --- Order matters. See §5.1 for the rationale. ---

  // 1. Single rep FIRST. Preserves v1 behavior for bare INT
  //    (e.g. 'Deadlift: 5' → single_rep_set_, not weight_).
    INT rir_dash?                                           #single_rep_set_

  // 1.5 Single rep with weight (point 4): N.weight format (e.g., '20.14' = 20 reps at 14kg).
  //      Allows weights with or without K_UNIT: '20.14', '20.14k', '20.23.5k' all work.
  //      Placed before group_of_rep_set to give N.weight priority over N.reps interpretation.
  | INT DOT INT K_UNIT? rir_dash?                         #single_rep_with_weight_

  // 2. Weight SECOND (with optional nested set). Preserves v1 behavior for '80.5'
  //    (→ weight_, not group_of_rep_set). Bare comma-decimals ('62,5') also land here.
  | weight ':'? set_?                                       #weight_

  // 3. Whole set (3 components + optional RIR).
  | INT sep INT sep weight rir_dash?                        #whole_set_

  // 4. Fixed-reps multi-weight, v1 style (comma separator, dot decimals).
  //    Each weight may carry its own RIR, so the shared fixed-rep count applies
  //    to every weight: '10..50-4,65-4,65-3' == '10..50-4,10.65-4,10.65-3'.
  | INT double_sep fixed_rep_weight (COMMA fixed_rep_weight)* #fixed_reps_multiple_weight_v1

  // 5. Fixed-reps multi-weight, v2 style (slash separator, either decimal).
  | INT double_sep weight (SLASH weight)+ rir_dash?         #fixed_reps_multiple_weight_v2

  // 6. Whole-set with extra weights, v2 style (new in Phase 2).
  //    'set_ SLASH weight ...' left-recurses into another set_.
  | set_ SLASH weight (SLASH weight)* rir_dash?             #whole_set_multi_weight_v2

  // 7. Group of reps (2 components + optional RIR).
  | INT sep INT rir_dash?                                   #group_of_rep_set

  // 8. Compound (multiple sets). Last, as a catch-all.
  | set_ ','? set_                                          #multiple_set_
  ;
