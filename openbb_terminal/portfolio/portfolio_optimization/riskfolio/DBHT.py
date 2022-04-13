""""""  #
"""
Copyright (c) 2020-2022, Dany Cajas
All rights reserved.
This work is licensed under BSD 3-Clause "New" or "Revised" License.
License available at https://github.com/dcajasn/Riskfolio-Lib/blob/master/LICENSE.txt

This work is based on the code of Tomaso Aste available at
https://www.mathworks.com/matlabcentral/fileexchange/46750-dbht
"""

import numpy as np
import scipy.sparse as sp
from scipy.spatial.distance import squareform
from scipy.cluster.hierarchy import from_mlab_linkage, optimal_leaf_ordering


def DBHTs(D, S, leaf_order=True):
    r"""
    Perform Direct Bubble Hierarchical Tree (DBHT) clustering, a deterministic
    technique which only requires a similarity matrix S, and related
    dissimilarity matrix D. For more information see "Hierarchical information
    clustering by means of topologically embedded graphs." :cite:`d-Song`.
    This version makes extensive use of graph-theoretic filtering technique
    called Triangulated Maximally Filtered Graph (TMFG).

    Parameters
    ----------
    D : nd-array
        N x N dissimilarity matrix - e.g. a distance: D=pdist(data,'euclidean')
        and then D=squareform(D).

    S : nd-array
        N x N similarity matrix (non-negative)- e.g. correlation
        coefficient+1: S = 2-D**2/2 or another possible choice can be S =
        exp(-D).

    Returns
    -------
    T8 : DataFrame
        N x 1 cluster membership vector.
    Rpm : nd-array
        N x N adjacency matrix of Plannar Maximally Filtered
        Graph (PMFG).
    Adjv : nd-array
        Bubble cluster membership matrix from BubbleCluster8.
    Dpm : nd-array
        N x N shortest path length matrix of PMFG
    Mv : nd-array
        N x Nb bubble membership matrix. Nb(n,bi)=1 indicates vertex n
        is a vertex of bubble bi.
    Z : nd-array
        Linkage matrix using DBHT hierarchy.
    """

    (Rpm, _, _, _, _) = PMFG_T2s(S)
    Apm = Rpm.copy()
    Apm[Apm != 0] = D[Apm != 0].copy()
    (Dpm, _) = distance_wei(Apm)
    (H1, Hb, Mb, CliqList, Sb) = CliqHierarchyTree2s(Rpm, method1="uniqueroot")
    del H1, Sb
    Mb = Mb[0 : CliqList.shape[0], :]
    Mv = np.empty((Rpm.shape[0], 0))
    for i in range(0, Mb.shape[1]):
        vec = np.zeros(Rpm.shape[0])
        vec[np.int32(np.unique(CliqList[Mb[:, i] != 0, :]))] = 1
        Mv = np.hstack((Mv, vec.reshape(-1, 1)))

    (Adjv, T8) = BubbleCluster8s(Rpm, Dpm, Hb, Mb, Mv, CliqList)
    Z = HierarchyConstruct4s(Rpm, Dpm, T8, Adjv, Mv)

    if leaf_order == True:
        Z = optimal_leaf_ordering(Z, squareform(D))

    return (T8, Rpm, Adjv, Dpm, Mv, Z)


def j_LoGo(S, separators, cliques):
    r"""
    computes sparse inverse covariance, J, from a clique tree made of cliques
    and separators. For more information see: :cite:`d-jLogo`.


    Parameters
    ----------
    S : ndarray
        It is the complete covariance matrix.
    separators : nd-array
        It is the list of separators.
    clique : nd-array
        It is the list of cliques.

    Returns
    -------
    JLogo : nd-array
        Inverse covariance.

    Notes
    -----
    separators and cliques can be the outputs of TMFG function

    """
    N = S.shape[0]
    if isinstance(separators, dict) == False:
        separators_temp = {}
        for i in range(len(separators)):
            separators_temp[i] = separators[i, :]

    if isinstance(cliques, dict) == False:
        cliques_temp = {}
        for i in range(len(cliques)):
            cliques_temp[i] = cliques[i, :]

    Jlogo = np.zeros((N, N))
    for i in cliques_temp.keys():
        v = np.int32(cliques_temp[i])
        Jlogo[np.ix_(v, v)] = Jlogo[np.ix_(v, v)] + np.linalg.inv(S[np.ix_(v, v)])

    for i in separators_temp.keys():
        v = np.int32(separators_temp[i])
        Jlogo[np.ix_(v, v)] = Jlogo[np.ix_(v, v)] - np.linalg.inv(S[np.ix_(v, v)])

    return Jlogo


def PMFG_T2s(W, nargout=3):
    r"""
    Computes a Triangulated Maximally Filtered Graph (TMFG) :cite:`d-Massara`
    starting from a tetrahedron and inserting recursively vertices inside
    existing triangles (T2 move) in order to approximate a maximal planar
    graph with the largest total weight - non negative weights.

    Parameters
    ----------
    W : nd-array
        An N x N matrix of non-negative weights.
    nargout : int, optional
        Number of results, posible values are 3, 4 and 5.

    Returns
    -------
    A : nd-array
        Adjacency matrix of the PMFG (with weights)
    tri : nd-array
        Matrix of triangles (triangular faces) of size 2N - 4 x 3
    separators : nd-array
        Matrix of 3-cliques that are not triangular faces (all 3-cliques are
        given by: [tri;separators]).
    clique4 : nd-array, optional
        List of all 4-cliques.
    cliqueTree : nd-array, optional
        4-cliques tree structure (adjacency matrix).

    """
    N = W.shape[0]
    if N < 9:
        print("W Matrix too small \n")
    if np.any(W < 0):
        print("W Matrix has negative elements! \n")

    A = np.zeros((N, N))  # ininzialize adjacency matrix
    in_v = -1 * np.ones(N, dtype=np.int32)  # ininzialize list of inserted vertices
    tri = np.zeros((2 * N - 4, 3))  # ininzialize list of triangles
    separators = np.zeros(
        (N - 4, 3)
    )  # ininzialize list of 3-cliques (non face-triangles)
    # find 3 vertices with largest strength
    s = np.sum(W * (W > np.mean(W)), axis=1)
    j = np.int32(np.argsort(s)[::-1].reshape(-1))

    in_v[0:4] = j[0:4]
    ou_v = np.setdiff1d(np.arange(0, N), in_v)  # list of vertices not inserted yet
    # build the tetrahedron with largest strength
    tri[0, :] = in_v[[0, 1, 2]]
    tri[1, :] = in_v[[1, 2, 3]]
    tri[2, :] = in_v[[0, 1, 3]]
    tri[3, :] = in_v[[0, 2, 3]]
    A[in_v[0], in_v[1]] = 1
    A[in_v[0], in_v[2]] = 1
    A[in_v[0], in_v[3]] = 1
    A[in_v[1], in_v[2]] = 1
    A[in_v[1], in_v[3]] = 1
    A[in_v[2], in_v[3]] = 1
    # build initial gain table
    gain = np.zeros((N, 2 * N - 4))
    gain[ou_v, 0] = np.sum(W[np.ix_(ou_v, np.int32(tri[0, :]))], axis=1)
    gain[ou_v, 1] = np.sum(W[np.ix_(ou_v, np.int32(tri[1, :]))], axis=1)
    gain[ou_v, 2] = np.sum(W[np.ix_(ou_v, np.int32(tri[2, :]))], axis=1)
    gain[ou_v, 3] = np.sum(W[np.ix_(ou_v, np.int32(tri[3, :]))], axis=1)

    kk = 3  # number of triangles
    for k in range(4, N):
        # find best vertex to add in a triangle
        if len(ou_v) == 1:  # special case for the last vertex
            ve = ou_v[0]
            v = 0
            tr = np.argmax(gain[ou_v, :])
        else:
            gij = np.max(gain[ou_v, :], axis=0)
            v = np.argmax(gain[ou_v, :], axis=0)
            tr = np.argmax(np.round(gij, 6).flatten())
            ve = ou_v[v[tr]]
            v = v[tr]

        # update vertex lists
        ou_v = ou_v[np.delete(np.arange(len(ou_v)), v)]
        in_v[k] = ve
        # update adjacency matrix
        A[np.ix_([ve], np.int32(tri[tr, :]))] = 1
        # update 3-clique list
        separators[k - 4, :] = tri[tr, :]
        # update triangle list replacing 1 and adding 2 triangles
        tri[kk + 1, :] = np.hstack((tri[tr, [0, 2]], ve))  # add
        tri[kk + 2, :] = np.hstack((tri[tr, [1, 2]], ve))  # add
        tri[tr, :] = np.hstack((tri[tr, [0, 1]], ve))  # replace
        # update gain table
        gain[ve, :] = 0
        gain[ou_v, tr] = np.sum(W[np.ix_(ou_v, np.int32(tri[tr, :]))], axis=1)
        gain[ou_v, kk + 1] = np.sum(W[np.ix_(ou_v, np.int32(tri[kk + 1, :]))], axis=1)
        gain[ou_v, kk + 2] = np.sum(W[np.ix_(ou_v, np.int32(tri[kk + 2, :]))], axis=1)
        # update number of triangles
        kk = kk + 2
        if np.mod(k, 1000) == 0:
            print("PMFG T2: %0.2f per-cent done\n", k / N * 100)

    A = W * ((A + A.T) == 1)

    if nargout > 3:
        cliques = np.vstack(
            (in_v[0:4].reshape(1, -1), np.hstack((separators, in_v[4:].reshape(-1, 1))))
        )
    else:
        cliques = None

    # computes 4-clique tree (note this may include incomplete cliques!)
    if nargout > 4:
        cliqueTree = np.zeros((cliques.shape[0], cliques.shape[0]))
        for i in range(0, cliques.shape[0]):
            ss = np.zeros(cliques.shape[0], 1)
            for k in range(0, 3):
                ss = ss + np.sum((cliques[i, k] == cliques), axis=1)

            cliqueTree[i, ss == 2] = 1
    else:
        cliqueTree = None

    return (A, tri, separators, cliques, cliqueTree)


def distance_wei(L):
    r"""
    The distance matrix contains lengths of shortest paths between all
    pairs of nodes. An entry (u,v) represents the length of shortest path
    from node u to node v. The average shortest path length is the
    characteristic path length of the network.

    Parameters
    ----------
    L : nd-array
        Directed/undirected connection-length matrix.

    Returns
    -------
    D : nd-array
        Distance (shortest weighted path) matrix
    B : nd-array
        Number of edges in shortest weighted path matrix

    Notes
    -----
    The input matrix must be a connection-length matrix, typically
    obtained via a mapping from weight to length. For instance, in a
    weighted correlation network higher correlations are more naturally
    interpreted as shorter distances and the input matrix should
    consequently be some inverse of the connectivity matrix.
    The number of edges in shortest weighted paths may in general
    exceed the number of edges in shortest binary paths (i.e. shortest
    paths computed on the binarized connectivity matrix), because shortest
    weighted paths have the minimal weighted distance, but not necessarily
    the minimal number of edges.

    Lengths between disconnected nodes are set to Inf.
    Lengths on the main diagonal are set to 0.

    Algorithm\: Dijkstra's algorithm.

    Mika Rubinov, UNSW/U Cambridge, 2007-2012.
    Rick Betzel and Andrea Avena, IU, 2012
    Modification history \:
    2007: original (MR)
    2009-08-04: min() function vectorized (MR)
    2012: added number of edges in shortest path as additional output (RB/AA)
    2013: variable names changed for consistency with other functions (MR)

    """

    n = len(L)
    D = np.ones((n, n)) * np.inf
    np.fill_diagonal(D, 0)  # distance matrix
    B = np.zeros((n, n))  # number of edges matrix
    for u in range(0, n):
        S = np.full(n, True, dtype=bool)  # distance permanence (true is temporary)
        L1 = L.copy()
        V = np.array([u])
        while 1:
            S[V] = False  # distance u->V is now permanent
            L1[:, V] = 0  # no in-edges as already shortest
            for v in V.tolist():
                # T = np.ravel(np.argwhere(L1[v, :]))  # neighbours of shortest nodes
                (_, T, _) = sp.find(L1[v, :])  # neighbours of shortest nodes
                d = np.min(
                    np.vstack(
                        (D[np.ix_([u], T)], D[np.ix_([u], [v])] + L1[np.ix_([v], T)])
                    ),
                    axis=0,
                )
                wi = np.argmin(
                    np.vstack(
                        (D[np.ix_([u], T)], D[np.ix_([u], [v])] + L1[np.ix_([v], T)])
                    ),
                    axis=0,
                )
                D[np.ix_([u], T)] = d  # smallest of old/new path lengths
                ind = T[wi == 2]  # indices of lengthened paths
                B[u, ind] = B[u, v] + 1  # increment no. of edges in lengthened paths

            if D[u, S].size == 0:
                minD = np.empty((0, 0))
            else:
                minD = np.min(D[u, S])
                minD = np.array([minD])

            if minD.shape[0] == 0 or np.isinf(minD):
                # isempty: all nodes reached; isinf: some nodes cannot be reached
                break
            V = np.ravel(np.argwhere(D[u, :] == minD))

    return (D, B)


def CliqHierarchyTree2s(Apm, method1):
    r"""
    ClqHierarchyTree2 looks for 3-cliques of a maximal planar graph, then
    construct hierarchy of the cliques with the definition of 'inside' a
    clique to be a subgraph with smaller size, when the entire graph is
    made disjoint by removing the clique :cite:`d-Song2`.

    Parameters
    ----------
    Apm : N
        N x N Adjacency matrix of a maximal planar graph.

    method1 : str
        Choose between 'uniqueroot' and 'equalroot'. Assigns connections
        between final root cliques. Uses Voronoi tesselation between tiling
        triangles.

    Returns
    -------
    H1 : nd-array
        Nc x Nc adjacency matrix for 3-clique hierarchical tree where Nc is
        the number of 3-cliques.
    H2 : nd-array
        Nb x Nb adjacency matrix for bubble hierarchical tree where Nb is the
        number of bubbles.
    Mb : nd-array
        Nc x Nb matrix bubble membership matrix. Mb(n,bi)=1 indicates that
        3-clique n belongs to bi bubble.
    CliqList : nd-array
        Nc x 3 matrix. Each row vector lists three vertices consisting a
        3-clique in the maximal planar graph.
    Sb : nd-array
        Nc x 1 vector. Sb(n)=1 indicates nth 3-clique is separating.
    """
    N = Apm.shape[0]
    # IndxTotal=1:N;
    if sp.issparse(Apm) != 1:
        A = 1.0 * sp.csr_matrix(Apm != 0).toarray()
    else:
        A = 1.0 * (Apm != 0)

    (K3, E, clique) = clique3(A)
    del K3, E  # , N3

    Nc = clique.shape[0]
    M = np.zeros((N, Nc))
    CliqList = clique.copy()
    Sb = np.zeros(Nc)
    del clique
    for n in range(0, Nc):
        cliq_vec = CliqList[n, :]
        (T, IndxNot) = FindDisjoint(A, cliq_vec)
        indx0 = np.argwhere(np.ravel(T) == 0)
        indx1 = np.argwhere(np.ravel(T) == 1)
        indx2 = np.argwhere(np.ravel(T) == 2)
        if len(indx1) > len(indx2):
            indx_s = np.vstack((indx2, indx0))
            del indx1, indx2
        else:
            indx_s = np.vstack((indx1, indx0))
            del indx1, indx2

        if (indx_s.shape[0] == 0) == 1:
            Sb[n] = 0
        else:
            Sb[n] = len(indx_s) - 3  # -3

        M[indx_s, n] = 1
        # del Indicator, InsideCliq, count, T, Temp, cliq_vec, IndxNot, InsideCliq
        del T, cliq_vec, IndxNot

    Pred = BuildHierarchy(M)
    Root = np.argwhere(Pred == -1)
    # for n=1:length(Root);
    #     Components{n}=find(M(:,Root(n))==1);
    # end
    del n

    if method1.lower() == "uniqueroot":

        if len(Root) > 1:
            Pred = np.append(Pred[:], -1)
            Pred[Root] = len(Pred) - 1

        H = np.zeros((Nc + 1, Nc + 1))
        for n in range(0, len(Pred)):
            if Pred[n] != -1:
                H[n, np.int32(Pred[n])] = 1

        H = H + H.T
    elif method1.lower() == "equalroot":
        if len(Root) > 1:
            # %RootCliq=CliqList(Root,:);
            Adj = AdjCliq(A, CliqList, Root)
        H = np.zeros((Nc, Nc))
        for n in range(0, len(Pred)):
            if Pred[n] != -1:
                H[n, np.int32(Pred[n])] = 1
        if (Pred.shape[0] == 0) != 1:
            H = H + H.T
            H = H + Adj
        else:
            H = np.empty((0, 0))

    H1 = H.copy()

    if (H1.shape[0] == 0) != 1:
        (H2, Mb) = BubbleHierarchy(Pred, Sb, A, CliqList)
    else:
        H2 = np.empty((0, 0))
        Mb = np.empty((0, 0))

    H2 = 1.0 * (H2 != 0)
    Mb = Mb[0 : CliqList.shape[0], :]

    return (H1, H2, Mb, CliqList, Sb)


def BuildHierarchy(M):
    Pred = -1 * np.ones(M.shape[1])
    for n in range(0, M.shape[1]):
        # Children = np.argwhere(np.ravel(M[:, n]) == 1)
        (_, Children, _) = sp.find(M[:, n] == 1)
        ChildrenSum = np.sum(M[Children, :], axis=0)
        Parents = np.argwhere(np.ravel(ChildrenSum) == len(Children))
        Parents = Parents[Parents != n]
        if (Parents.shape[0] == 0) != 1:
            ParentSum = np.sum(M[:, Parents], axis=0)
            a = np.argwhere(ParentSum == np.min(ParentSum))
            if len(a) == 1:
                Pred[n] = Parents[a]
            else:
                Pred = np.empty(0)
                break
        else:
            Pred[n] = -1

    return Pred


def FindDisjoint(Adj, Cliq):
    N = Adj.shape[0]
    Temp = Adj.copy()
    T = np.zeros(N)
    IndxTotal = np.arange(0, N)
    IndxNot = np.argwhere(
        np.logical_and(IndxTotal != Cliq[0], IndxTotal != Cliq[1], IndxTotal != Cliq[2])
    )
    Temp[np.int32(Cliq), :] = 0
    Temp[:, np.int32(Cliq)] = 0
    # %d = bfs(Temp,IndxNot(1));
    (d, _) = breadth(Temp, IndxNot[0])
    d[np.isinf(d)] = -1
    d[IndxNot[0]] = 0
    Indx1 = d == -1
    Indx2 = d != -1
    T[Indx1] = 1
    T[Indx2] = 2
    T[np.int32(Cliq)] = 0
    del Temp

    return (T, IndxNot)


def AdjCliq(A, CliqList, CliqRoot):
    Nc = CliqList.shape[0]
    CliqList_temp = np.int32(CliqList.copy())
    CliqRoot_temp = np.int32(np.ravel(CliqRoot))
    N = A.shape[0]
    Adj = np.zeros((Nc, Nc))
    Indicator = np.zeros((N, 1))
    for n in range(0, len(CliqRoot_temp)):
        Indicator[CliqList_temp[CliqRoot_temp[n], :]] = 1
        Indi = np.hstack(
            (
                Indicator[CliqList_temp[CliqRoot_temp, 0], 0],
                Indicator[CliqList_temp[CliqRoot_temp, 1], 0],
                Indicator[CliqList_temp[CliqRoot_temp, 2], 0],
            )
        )
        adjacent = CliqRoot_temp[np.sum(Indi.T, axis=0) == 1]
        Adj[adjacent, n] = 0

    Adj = Adj + Adj.T

    return Adj


def BubbleHierarchy(Pred, Sb, A, CliqList):
    Nc = Pred.shape[0]
    Root = np.argwhere(Pred == -1)
    CliqCount = np.zeros(Nc)
    CliqCount[Root] = 1
    Mb = np.empty((Nc, 0))

    if len(Root) > 1:
        TempVec = np.zeros((Nc, 1))
        TempVec[Root] = 1
        Mb = np.hstack((Mb, TempVec))
        del TempVec

    while np.sum(CliqCount) < Nc:
        NxtRoot = np.empty((0, 1))

        for n in range(0, len(Root)):
            # DirectChild = np.ravel(np.argwhere(Pred == Root[n]))
            (_, DirectChild, _) = sp.find(Pred == Root[n])
            TempVec = np.zeros((Nc, 1))
            TempVec[np.append(DirectChild, np.int32(Root[n])), 0] = 1
            Mb = np.hstack((Mb, TempVec))
            CliqCount[DirectChild] = 1

            for m in range(0, len(DirectChild)):
                if Sb[DirectChild[m]] != 0:
                    NxtRoot = np.vstack((NxtRoot, DirectChild[m]))

            del DirectChild, TempVec

        Root = np.unique(NxtRoot)

    Nb = Mb.shape[1]
    H = np.zeros((Nb, Nb))

    # if sum(IdentifyJoint==0)==0;
    for n in range(0, Nb):
        Indx = Mb[:, n] == 1
        JointSum = np.sum(Mb[Indx, :], axis=0)
        Neigh = JointSum >= 1
        H[n, Neigh] = 1
    # else
    #     H=[];

    H = H + H.T
    H = H - np.diag(np.diag(H))

    return (H, Mb)


def clique3(A):
    r"""
    Computes the list of 3-cliques.

    Parameters
    ----------
    A : nd-array
        N x N sparse adjacency matrix.

    Returns
    -------
    clique : nd-array
        Nc x 3 matrix. Each row vector contains the list of vertices for
        a 3-clique.
    """

    A = A - np.diag(np.diag(A))
    A = 1.0 * (A != 0)
    A2 = A @ A
    P = (1.0 * (A2 != 0)) * (1.0 * (A != 0))

    P = sp.csr_matrix(np.triu(P))

    (r, c, _) = sp.find(P != 0)
    E = np.hstack((r.reshape(-1, 1), c.reshape(-1, 1)))

    K3 = {}
    N3 = np.zeros(len(r))
    for n in range(0, len(r)):
        i = r[n]
        j = c[n]
        a = A[i, :] * A[j, :]
        # indx = np.ravel(np.argwhere(a != 0))
        (_, indx, _) = sp.find(a != 0)
        K3[n] = indx
        N3[n] = len(indx)

    clique = np.zeros((1, 3))
    for n in range(0, len(r)):
        temp = K3[n]
        for m in range(0, len(temp)):
            candidate = E[n, :]
            candidate = np.hstack((candidate, temp[m]))
            candidate = np.sort(candidate)
            a = 1 * (clique[:, 0] == candidate[0])
            b = 1 * (clique[:, 1] == candidate[1])
            c = 1 * (clique[:, 2] == candidate[2])
            check = (a * b) * c
            check = np.sum(check)
            if check == 0:
                clique = np.vstack((clique, candidate.reshape(1, -1)))
            del candidate, check, a, b, c

    isort = np.lexsort((clique[:, 2], clique[:, 1], clique[:, 0]))

    clique = clique[isort]
    clique = clique[1 : clique.shape[0], :]

    return (K3, E, clique)


def breadth(CIJ, source):
    r"""
    Implementation of breadth-first search.

    Parameters
    ----------
    CIJ : nd-array
        Binary (directed/undirected) connection matrix
    source : nd-array
        Source vertex

    Returns
    -------
    distance : nd-array
        Distance between 'source' and i'th vertex (0 for source vertex).
    branch : nd-array
        Vertex that precedes i in the breadth-first search tree (-1 for source
        vertex)

    Notes
    -----
    Breadth-first search tree does not contain all paths (or all shortest
    paths), but allows the determination of at least one path with minimum
    distance. The entire graph is explored, starting from source vertex
    'source'.

    Olaf Sporns, Indiana University, 2002/2007/2008
    """

    N = CIJ.shape[0]
    # colors: white, gray, black
    white = 0
    gray = 1
    black = 2
    # initialize colors
    color = np.zeros(N)
    # initialize distances
    distance = np.inf * np.ones(N)
    # initialize branches
    branch = np.zeros(N)
    # start on vertex 'source'
    color[source] = gray
    distance[source] = 0
    branch[source] = -1
    Q = np.array(source).reshape(-1)
    # keep going until the entire graph is explored
    while (Q.shape[0] == 0) == 0:
        u = Q[0]
        # ns = np.argwhere(CIJ[u, :])
        (_, ns, _) = sp.find(CIJ[u, :])
        for v in ns:
            # this allows the 'source' distance to itself to be recorded
            if distance[v].all() == 0:
                distance[v] = distance[u] + 1
            if color[v].all() == white:
                color[v] = gray
                distance[v] = distance[u] + 1
                branch[v] = u
                Q = np.hstack((Q, v))

        Q = Q[1 : len(Q)]
        color[u] = black

    return (distance, branch)


def BubbleCluster8s(Rpm, Dpm, Hb, Mb, Mv, CliqList):
    r"""
    Obtains non-discrete and discrete clusterings from the bubble topology of
    PMFG.

    Parameters
    ----------
    Rpm : nd-array
        N x N sparse weighted adjacency matrix of PMFG.
    Dpm : nd-array
        N x N shortest path lengths matrix of PMFG
    Hb : nd-array
        Undirected bubble tree of PMFG
    Mb : nd-array
        Nc x Nb bubble membership matrix for 3-cliques. Mb(n,bi)=1 indicates
        that 3-clique n belongs to bi bubble.
    Mv : nd-array
        N x Nb bubble membership matrix for vertices.
    CliqList : nd-array
        Nc x 3 matrix of list of 3-cliques. Each row vector contains the list
        of vertices for a particular 3-clique.

    Returns
    -------
    Adjv : nd-array
        N x Nk cluster membership matrix for vertices for non-discrete
        clustering via the bubble topology. Adjv(n,k)=1 indicates cluster
        membership of vertex n to kth non-discrete cluster.
    Tc : nd-array
        N x 1 cluster membership vector. Tc(n)=k indicates cluster membership
        of vertex n to kth discrete cluster.
    """

    (Hc, Sep) = DirectHb(
        Rpm, Hb, Mb, Mv, CliqList
    )  # Assign directions on the bubble tree
    N = Rpm.shape[0]  # Number of vertices in the PMFG
    # indx = np.ravel(np.argwhere(Sep == 1))  # Look for the converging bubbles
    (_, indx, _) = sp.find(Sep == 1)  # Look for the converging bubbles
    Adjv = np.empty((0, 0))
    if len(indx) > 1:
        Adjv = np.zeros(
            (Mv.shape[0], len(indx))
        )  # Set the non-discrete cluster membership matrix 'Adjv' at default
        # Identify the non-discrete cluster membership of vertices by each
        # converging bubble
        for n in range(0, len(indx)):
            # %[d dt p]=bfs(Hc.T, indx[n]);
            (d, _) = breadth(Hc.T, indx[n])
            d[np.isinf(d)] = -1
            d[indx[n]] = 0
            (r, c, _) = sp.find(Mv[:, d != -1] != 0)
            Adjv[np.unique(r), n] = 1
            del d, r, c  #%, dt, p

        Tc = -1 * np.ones(N)  # Set the discrete cluster membership vector at default
        Bubv = Mv[:, indx]  # Gather the list of vertices in the converging bubbles
        (_, cv, _) = sp.find(
            np.sum(Bubv.T, axis=0).T == 1
        )  # Identify vertices which belong to single converging bubbles
        (_, uv, _) = sp.find(
            np.sum(Bubv.T, axis=0).T > 1
        )  # Identify vertices which belong to more than one converging bubbles.
        Mdjv = np.zeros(
            (N, len(indx))
        )  # Set the cluster membership matrix for vertices in the converging bubbles at default
        Mdjv[cv, :] = Bubv[
            cv, :
        ].copy()  # Assign vertices which belong to single converging bubbles to the rightful clusters.
        # Assign converging bubble membership of vertices in `uv'
        for v in range(0, len(uv)):
            v_cont = np.sum(Rpm[:, uv[v]].reshape(-1, 1) * Bubv, axis=0).reshape(
                -1, 1
            )  # sum of edge weights linked to uv(v) in each converging bubble
            all_cont = 3 * (
                np.sum(Bubv, axis=0) - 2
            )  # number of edges in converging bubble
            all_cont = all_cont.reshape(-1, 1)
            imx = np.argmax(v_cont / all_cont)
            Mdjv[uv[v], imx] = 1  # Pick the most strongly associated converging bubble

        (v, ci, _) = sp.find(1 * (Mdjv != 0))
        Tc[v] = ci
        del (
            v,
            ci,
        )  # Assign discrete cluster membership of vertices in the converging bubbles.

        Udjv = Dpm @ (Mdjv @ np.diag(1 / np.sum(1 * (Mdjv != 0), axis=0)))
        Udjv[
            Adjv == 0
        ] = np.inf  # Compute the distance between a vertex and the converging bubbles.
        # mn = np.min(Udjv[np.sum(Mdjv.T, axis=0)==0,:].T) # Look for the closest converging bubble
        imn = np.argmin(Udjv[np.sum(Mdjv, axis=1) == 0, :], axis=1)
        Tc[
            Tc == -1
        ] = imn  # Assign discrete cluster membership according to the distances to the converging bubbles
    else:
        Tc = np.ones(
            N
        )  # if there is one converging bubble, all vertices belong to a single cluster

    return (Adjv, Tc)


def DirectHb(Rpm, Hb, Mb, Mv, CliqList):
    r"""
    Computes directions on each separating 3-clique of a maximal planar
    graph, hence computes Directed Bubble Hierarchical Tree (DBHT).

    Parameters
    ----------
    Rpm : nd-array
        N x N sparse weighted adjacency matrix of PMFG
    Hb : nd-array
        Undirected bubble tree of PMFG
    Mb : nd-array
        Nc x Nb bubble membership matrix for 3-cliques. Mb(n,bi)=1 indicates
        that 3-clique n belongs to bi bubble.
    Mv : nd-array
        N x Nb bubble membership matrix for vertices.
    CliqList : nd-array
        Nc x 3 matrix of list of 3-cliques. Each row vector contains the list
        of vertices for a particular 3-clique.

    Returns
    -------
    Hc : nd-array
        Nb x Nb unweighted directed adjacency matrix of DBHT. Hc(i,j)=1
        indicates a directed edge from bubble i to bubble j.
    """

    Hb_temp = 1 * (Hb != 0)
    (r, c, _) = sp.find(sp.triu(sp.csr_matrix(Hb_temp)) != 0)
    CliqEdge = np.empty((0, 3))
    for n in range(0, len(r)):
        data = np.argwhere(np.logical_and(Mb[:, r[n]] != 0, Mb[:, c[n]] != 0))
        if data.shape[0] != 0:
            data = np.hstack((r[n].reshape(1, -1), c[n].reshape(1, -1), data))
            CliqEdge = np.vstack((CliqEdge, data))

    del r, c

    kb = np.sum(1 * (Hb_temp != 0), axis=0)
    Hc = np.zeros((Mv.shape[1], Mv.shape[1]))
    CliqEdge = np.int32(CliqEdge)

    for n in range(0, CliqEdge.shape[0]):
        Temp = Hb_temp.copy()
        Temp[CliqEdge[n, 0], CliqEdge[n, 1]] = 0
        Temp[CliqEdge[n, 1], CliqEdge[n, 0]] = 0
        (d, _) = breadth(Temp, np.array([0]))
        d[np.isinf(d)] = -1
        d[0] = 0
        vo = np.int32(CliqList[CliqEdge[n, 2], :])
        bleft = CliqEdge[n, 0:2]
        bleft = bleft[d[bleft] != -1]
        bright = CliqEdge[n, 0:2]
        bright = bright[d[bright] == -1]
        vleftc = np.argwhere(Mv[:, d != -1] != 0)
        vleft = vleftc[:, 0]
        c = vleftc[:, 1]
        vleft = np.setdiff1d(vleft, vo)
        vrightc = np.argwhere(Mv[:, d == -1] != 0)
        vright = vrightc[:, 0]
        c = vrightc[:, 1]
        vright = np.setdiff1d(vright, vo)
        del c
        left = np.sum(Rpm[np.ix_(vo, vleft)])
        right = np.sum(Rpm[np.ix_(vo, vright)])
        if left > right:
            Hc[np.ix_(bright, bleft)] = left
        else:
            Hc[np.ix_(bleft, bright)] = right
        del vleft, vright, vo, Temp, bleft, bright, right, left

    Sep = np.double((np.sum(Hc.T, axis=0) == 0))
    # Sep[(np.sum(Hc, axis=0) == 0) & (kb > 1)] = 2
    Sep[np.logical_and(np.sum(Hc, axis=0) == 0, kb > 1)] = 2

    return (Hc, Sep)


def HierarchyConstruct4s(Rpm, Dpm, Tc, Adjv, Mv):
    r"""
    Constructs intra- and inter-cluster hierarchy by utilizing Bubble
    hierarchy structure of a maximal planar graph, namely Planar Maximally
    Filtered Graph (PMFG).

    Parameters
    ----------
    Rpm : nd-array
        N x N Weighted adjacency matrix of PMFG.
    Dpm : nd-array
        N x N shortest path length matrix of PMFG.
    Tc : nd-array
        N x 1 cluster membership vector from DBHT clustering. Tc(n)=z_i
        indicate cluster of nth vertex.
    Adjv : nd-array
        Bubble cluster membership matrix from BubbleCluster8s.
    Mv : nd-array
        Bubble membership of vertices from BubbleCluster8s.

    Returns
    -------
    Z : nd-array
        (N-1) x 4 linkage matrix, in the same format as the output from matlab
        function 'linkage'.
    """

    N = Dpm.shape[0]
    kvec = np.int32(np.unique(Tc))
    LabelVec1 = np.arange(0, N)
    # LinkageDist = np.zeros((1,1))
    E = sp.csr_matrix(
        (np.ones(N), (np.arange(0, N), np.int32(Tc))),
        shape=(N, np.int32(np.max(Tc) + 1)),
    ).toarray()
    Z = np.array(np.empty((0, 3)))
    Tc = Tc + 1
    kvec = kvec + 1
    # Intra-cluster hierarchy construction
    for n in range(0, len(kvec)):
        Mc = (
            E[:, kvec[n] - 1].reshape(-1, 1) * Mv
        )  # Get the list of bubbles which coincide with nth cluster
        Mvv = BubbleMember(
            Dpm, Rpm, Mv, Mc
        )  # Assign each vertex in the nth cluster to a specific bubble.
        (_, Bub, _) = sp.find(
            np.sum(Mvv, axis=0) > 0
        )  # Get the list of bubbles which contain the vertices of nth cluster
        nc = np.sum(Tc == kvec[n], axis=0) - 1  ##########
        # %Apply the linkage within the bubbles.
        for m in range(0, len(Bub)):
            (_, V, _) = sp.find(
                Mvv[:, Bub[m]] != 0
            )  # Retrieve the list of vertices assigned to mth bubble.
            if len(V) > 1:
                dpm = Dpm[
                    np.ix_(V, V)
                ]  # Retrieve the distance matrix for the vertices in V
                LabelVec = LabelVec1[
                    V
                ]  # Initiate the label vector which labels for the clusters.
                LabelVec2 = LabelVec1.copy()
                for v in range(0, len(V) - 1):
                    (PairLink, dvu) = LinkageFunction(
                        dpm, LabelVec
                    )  # Look for the pair of clusters which produces the best linkage
                    LabelVec[
                        np.logical_or(LabelVec == PairLink[0], LabelVec == PairLink[1])
                    ] = (
                        np.max(LabelVec1, axis=0) + 1
                    )  # Merge the cluster pair by updating the label vector with a same label.
                    LabelVec2[V] = LabelVec.copy()
                    Z = DendroConstruct(Z, LabelVec1, LabelVec2, 1 / nc)
                    nc = nc - 1
                    LabelVec1 = LabelVec2.copy()
                    del PairLink, dvu  # , Vect
                del LabelVec, dpm, LabelVec2
            del V

        (_, V, _) = sp.find(E[:, kvec[n] - 1] != 0)
        dpm = Dpm[np.ix_(V, V)]
        # %Perform linkage merging between the bubbles
        LabelVec = LabelVec1[
            V
        ]  # Initiate the label vector which labels for the clusters.
        LabelVec2 = LabelVec1.copy()
        for b in range(0, len(Bub) - 1):
            (PairLink, dvu) = LinkageFunction(dpm, LabelVec)
            # %[PairLink,dvu]=LinkageFunction(rpm,LabelVec);
            LabelVec[
                np.logical_or(LabelVec == PairLink[0], LabelVec == PairLink[1])
            ] = (
                np.max(LabelVec1) + 1
            )  # Merge the cluster pair by updating the label vector with a same label.
            LabelVec2[V] = LabelVec.copy()
            Z = DendroConstruct(Z, LabelVec1, LabelVec2, 1 / nc)
            nc = nc - 1
            LabelVec1 = LabelVec2.copy()
            del PairLink, dvu  # , Vect

        del LabelVec, V, dpm, LabelVec2  # , rpm,

    # %Inter-cluster hierarchy construction
    LabelVec2 = LabelVec1.copy()
    dcl = np.ones(len(LabelVec1))
    for n in range(0, len(kvec) - 1):
        (PairLink, dvu) = LinkageFunction(Dpm, LabelVec1)
        # %[PairLink,dvu]=LinkageFunction(Rpm,LabelVec);
        LabelVec2[np.logical_or(LabelVec1 == PairLink[0], LabelVec1 == PairLink[1])] = (
            np.max(LabelVec1, axis=0) + 1
        )  # Merge the cluster pair by updating the label vector with a same label.
        dvu = np.unique(dcl[LabelVec1 == PairLink[0]]) + np.unique(
            dcl[LabelVec1 == PairLink[1]]
        )
        dcl[np.logical_or(LabelVec1 == PairLink[0], LabelVec1 == PairLink[1])] = dvu
        Z = DendroConstruct(Z, LabelVec1, LabelVec2, dvu)
        LabelVec1 = LabelVec2.copy()
        del PairLink, dvu
    del LabelVec1
    Z[:, 0:2] = Z[:, 0:2] + 1
    Z = from_mlab_linkage(Z)

    if len(np.unique(LabelVec2)) > 1:
        print("Something Wrong in Merging. Check the codes.")
        return None

    return Z


def LinkageFunction(d, labelvec):
    lvec = np.unique(labelvec)
    Links = np.empty((0, 3))
    for r in range(0, len(lvec) - 1):
        vecr = (labelvec == lvec[r]).reshape(-1)
        for c in range(r + 1, len(lvec)):
            vecc = (labelvec == lvec[c]).reshape(-1)
            x1 = np.ravel(np.logical_or(vecr, vecc))
            dd = d[np.ix_(x1, x1)]

            if dd[dd != 0].shape[0] == 0:
                Link1 = np.hstack((lvec[r], lvec[c], 0))
            else:
                Link1 = np.hstack((lvec[r], lvec[c], np.max(dd[dd != 0], axis=0)))
            Links = np.vstack((Links, Link1))
            del vecc

    dvu = np.min(Links[:, 2], axis=0)
    imn = np.argmin(Links[:, 2], axis=0)
    PairLink = Links[imn, 0:2]

    return (PairLink, dvu)


def BubbleMember(Dpm, Rpm, Mv, Mc):
    Mvv = np.zeros((Mv.shape[0], Mv.shape[1]))
    (_, vu, _) = sp.find(np.sum(Mc.T, axis=0) > 1)
    (_, v, _) = sp.find(np.sum(Mc.T, axis=0) == 1)
    Mvv[v, :] = Mc[v, :]
    for n in range(0, len(vu)):
        (_, bub, _) = sp.find(Mc[vu[n], :] != 0)
        vu_bub = np.sum(Rpm[:, vu[n]].reshape(-1, 1) * Mv[:, bub], axis=0).T
        all_bub = np.diag(Mv[:, bub].T @ Rpm @ Mv[:, bub]) / 2
        frac = vu_bub / all_bub
        # mx = np.max(frac, axis=0)
        imx = np.argmax(frac, axis=0)
        Mvv[vu[n], bub[imx]] = 1

    return Mvv


def DendroConstruct(Zi, LabelVec1, LabelVec2, LinkageDist):
    indx = (LabelVec1.T == LabelVec2.T) != 1
    if len(np.unique(LabelVec1[indx])) != 2:
        print("Check the codes")
        return

    Z = np.vstack((Zi, np.hstack((np.sort(np.unique(LabelVec1[indx])), LinkageDist))))

    return Z
