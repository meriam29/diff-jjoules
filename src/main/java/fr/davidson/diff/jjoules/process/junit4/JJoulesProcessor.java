package fr.davidson.diff.jjoules.process.junit4;

import spoon.processing.AbstractProcessor;
import spoon.reflect.code.CtInvocation;
import spoon.reflect.code.CtLiteral;
import spoon.reflect.code.CtTypeAccess;
import spoon.reflect.declaration.CtMethod;
import spoon.reflect.factory.Factory;
import spoon.reflect.reference.CtExecutableReference;
import spoon.reflect.reference.CtTypeReference;

import java.util.*;

/**
 * @author Benjamin DANGLOT
 * benjamin.danglot@davidson.fr
 * 27/11/2020
 */
public class JJoulesProcessor extends AbstractProcessor<CtMethod<?>> {

    private final Map<String, List<String>> testsToBeInstrumented;

    public JJoulesProcessor(final Map<String, List<String>> testsList) {
        this.testsToBeInstrumented = testsList;
    }

    @Override
    public boolean isToBeProcessed(CtMethod<?> candidate) {
        return candidate.getDeclaringType() != null &&
                this.testsToBeInstrumented.containsKey(candidate.getDeclaringType().getQualifiedName()) &&
                this.testsToBeInstrumented.get(
                        candidate.getDeclaringType().getQualifiedName()
                ).contains(candidate.getSimpleName());
    }

    @Override
    public void process(CtMethod<?> ctMethod) {
        System.out.println("Processing " + ctMethod.getDeclaringType().getQualifiedName() + "#" + ctMethod.getSimpleName());
        final Factory factory = ctMethod.getFactory();

        // target
        final CtTypeReference<?> energyTestReference = factory.Type().createReference("org.powerapi.jjoules.junit4.EnergyTest");
        final CtTypeAccess<?> typeAccess = factory.createTypeAccess(energyTestReference);

        // method to call
        final CtExecutableReference<?> beforeTestReference = factory.createExecutableReference();
        beforeTestReference.setDeclaringType(energyTestReference);
        beforeTestReference.setStatic(true);
        beforeTestReference.setSimpleName("beforeTest");
        final CtExecutableReference<?> afterTestReference = factory.createExecutableReference();
        afterTestReference.setStatic(true);
        afterTestReference.setDeclaringType(energyTestReference);
        afterTestReference.setSimpleName("afterTest");

        // parameters
        final CtLiteral<String> classNameLiteral = factory.createLiteral(ctMethod.getDeclaringType().getQualifiedName());
        final CtLiteral<String> testMethodNameLiteral = factory.createLiteral(ctMethod.getSimpleName());

        // Invocations
        final CtInvocation<?> beforeTestInvocation = factory.createInvocation(typeAccess, beforeTestReference, Arrays.asList(classNameLiteral, testMethodNameLiteral));
        final CtInvocation<?> afterTestInvocation = factory.createInvocation(typeAccess, afterTestReference);

        ctMethod.getBody().insertBegin(beforeTestInvocation);
        ctMethod.getBody().insertEnd(afterTestInvocation);
    }

}
