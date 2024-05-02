#include "llvm/Pass.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;

namespace {

struct SkeletonPass : public PassInfoMixin<SkeletonPass> {
  PreservedAnalyses run(Module &M, ModuleAnalysisManager &AM) {
    for (auto &F : M) {
      for (auto &B : F) {
        for (auto &I : B) {
          if (auto *op = dyn_cast<BinaryOperator>(&I)) {
            switch (op->getOpcode()) {
            case Instruction::Add:
              errs() << "+\n";
              break;
            case Instruction::Sub:
              errs() << "-\n";
              break;
            case Instruction::Mul:
              errs() << "*\n";
              break;
            case Instruction::SDiv:
              errs() << "/\n";
              break;

            default:
              break;
            }
          }
        }
      }
    }
    return PreservedAnalyses::all();
  };
};

} // namespace

// The pass must provide at least one of two entry points for the new pass
// manager, one for static registration and one for dynamically loaded plugins.
// This one is dynamically loaded plugins
extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo() {
  return {.APIVersion = LLVM_PLUGIN_API_VERSION,
          .PluginName = "Skeleton pass",
          .PluginVersion = "v0.1",
          .RegisterPassBuilderCallbacks = [](PassBuilder &PB) {
            PB.registerPipelineStartEPCallback(
                [](ModulePassManager &MPM, OptimizationLevel Level) {
                  MPM.addPass(SkeletonPass());
                });
          }};
}