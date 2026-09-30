# Generated from training.g4 by ANTLR 4.9.3
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .trainingParser import trainingParser
else:
    from trainingParser import trainingParser

# This class defines a complete generic visitor for a parse tree produced by trainingParser.

class trainingVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by trainingParser#workout.
    def visitWorkout(self, ctx:trainingParser.WorkoutContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by trainingParser#exercise_name.
    def visitExercise_name(self, ctx:trainingParser.Exercise_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by trainingParser#weight_com.
    def visitWeight_com(self, ctx:trainingParser.Weight_comContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by trainingParser#weight_dot.
    def visitWeight_dot(self, ctx:trainingParser.Weight_dotContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by trainingParser#weight.
    def visitWeight(self, ctx:trainingParser.WeightContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by trainingParser#exercise.
    def visitExercise(self, ctx:trainingParser.ExerciseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by trainingParser#sep.
    def visitSep(self, ctx:trainingParser.SepContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by trainingParser#double_sep.
    def visitDouble_sep(self, ctx:trainingParser.Double_sepContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by trainingParser#rir_dash.
    def visitRir_dash(self, ctx:trainingParser.Rir_dashContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by trainingParser#weight_.
    def visitWeight_(self, ctx:trainingParser.Weight_Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by trainingParser#multiple_set_.
    def visitMultiple_set_(self, ctx:trainingParser.Multiple_set_Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by trainingParser#group_of_rep_set.
    def visitGroup_of_rep_set(self, ctx:trainingParser.Group_of_rep_setContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by trainingParser#single_rep_set_.
    def visitSingle_rep_set_(self, ctx:trainingParser.Single_rep_set_Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by trainingParser#fixed_reps_multiple_weight_v2.
    def visitFixed_reps_multiple_weight_v2(self, ctx:trainingParser.Fixed_reps_multiple_weight_v2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by trainingParser#fixed_reps_multiple_weight_v1.
    def visitFixed_reps_multiple_weight_v1(self, ctx:trainingParser.Fixed_reps_multiple_weight_v1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by trainingParser#whole_set_multi_weight_v2.
    def visitWhole_set_multi_weight_v2(self, ctx:trainingParser.Whole_set_multi_weight_v2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by trainingParser#whole_set_.
    def visitWhole_set_(self, ctx:trainingParser.Whole_set_Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by trainingParser#single_rep_with_weight_.
    def visitSingle_rep_with_weight_(self, ctx:trainingParser.Single_rep_with_weight_Context):
        return self.visitChildren(ctx)



del trainingParser