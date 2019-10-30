from DistMethods.FlowVector import getRedistDict_Flow, setFlowVector, setStasisVector

def drivetest():
    n_keys = [1,2,3,4,5,6]
    n_benches = [0.1,0.1,0.2,0.2,0.3,0.4]
    btot = 1.3
    n_qls = [20,0,0,0,0,0]
    qltot = 20
    output = []
    output.append(getRedistDict_Flow(n_keys,n_benches,btot,n_qls,qltot))
    setFlowVector([-0.8, -0.6])
    output.append(getRedistDict_Flow(n_keys,n_benches,btot,n_qls,qltot))
    return output


if( __name__ == "__main__"):
    print(drivetest())
