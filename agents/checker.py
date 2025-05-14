import subprocess

class Checker:
    def compile(self, code: str, use_openmp: bool, src_dir: str):
        with open(f"{src_dir}\\temp.c","w") as f: f.write(code)
        cmd = ["gcc",f"{src_dir}\\temp.c","-o","temp","-O2"]
        if use_openmp: cmd.append("-fopenmp")
        result = subprocess.run(cmd, capture_output=True, text=True)
        return (result.returncode==0, result.stderr)
