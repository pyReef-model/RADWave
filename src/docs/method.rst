Altimeter data 2 wave climate
================

This page outlines the techniques and methods used to acquire and analyse data from *radar satellite altimeters* and how **RADWave** package uses this dataset to investigate wave parameters, enabling wave climate analysis of varying spatial and temporal resolution.

.. image:: ../RADWave/Notebooks/images/img1.jpg
   :scale: 10 %
   :alt: LEC versus diversity
   :align: center

.. important::
  **RADWave** uses post-processed altimeter dataset to analyse historical wave climate and trends but can also be used to determine cyclone-generated wave conditions.


Satellite Altimeter Data
-------------

Altimeter observations of the ocean surface are been recorded since 1985, with a short break between 1989-1991 due to no operating satellites [Chelton2001]_ (fig. below from (`source <http://www.altimetry.info/radar-altimetry-tutorial/how-altimetry-works/>`_)). Thirteen altimeters, named **GEOSAT**, **ERS-1**, **TOPEX**, **ERS-2**, **GFO**, **JASON-1**, **ENVISAT**, **JASON-2**, **HAI-YANG-2A**, **SARAL**, **JASON-3** and **SENTINEL-3A**, provides detailed and global coverage.

.. note::
 Satellites were predominantly placed in sun-synchronous, near-polar orbits, covering the same ground track every 3-10 days. Observations are therefore not made every day, however, observation frequency has increased in recent years due to the addition of more altimeters.

.. image:: ../RADWave/Notebooks/images/img3.jpg
  :scale: 8 %
  :alt: Altimeter data
  :align: center

.. attention:
 Twelve of the altimeters operate in the *Ku* frequency band, except for **SARAL**, which uses the *Ka* band.

To increase analysis ability between altimeter missions, [Ribal2019]_ combined and reprocessed data from *Globwave*, *Radar Altimeter Data System* and the *National Satellite Ocean Application Service* to provide a single dataset spanning all thirteen altimeter missions from 1985-2019.

> Altimeters measure the ocean surface by emitting a *radar pulse* and determining the shape, power and time delay of the return pulse. The shape is converted into **Hs**. The power of the return pulse, also known as the backscatter coefficient, is used to determine *ocean surface properties* including surface roughness. By applying a relationship between uncalibrated wind speed and backscatter coefficient, a **calibrated wind speed** (10 m above the sea surface and averaged over 10 minutes) can be determined.

.. important::
  Overall, [Ribal2019]_ suggests that preprocessed and calibrated dataset is valid for wind speed below 24 m/s and Hs below 9 m, however, notes that values above this limit are likely still valid.

`Dijkstra's algorithm`_
-----------------------

The estimation of :math:`C_{ji}` requires computation of **all the possible paths** *p* from *j* to *i* and is defined as the maximum closeness value along these paths and this is solved for each cell *j* using **Dijkstra's algorithm** [Dijkstra1959]_ with diagonal connectivity between cells.

For each cell *j*, the algorithm  builds a **Dijkstra tree** that branches the given cell with all the cells defining the simulated region. **Edge weights** are set equal to the square of the difference between the considered vertex elevation (:math:`z_{k_r}`) and :math:`z_j`. The least-cost distance between *j* and *i* is then calculated as the **minimum sum of edge weights** obtained from the cells along the shortest-path (see top figure).

Here, the closeness is measured as a **least-cost** distances that optimises the costs associated to the edge weights of the traversed cells as well as the travelled Euclidean distance. As the least-cost distances incorporate landscape costs to movement, the approach allows for **closeness differentiation** between cells that might be seen as *equally near* if landscape costs were not accounted for.

In **bioLEC** we rely on `scikit-image`_ to compute the least cost distances [Etherington2017]_. `scikit-image`_ package is primarily intended to process image [vanderWalt2014]_ but is designed to work with **NumPy arrays** making it compatible with other Python packages (*e.g.* most other geospatial Python packages) and really simple to use with digital elevation datasets.

While `scikit-image`_ uses slightly different terminology, talking about **minimum cost paths** rather than **least-cost paths**, the approach is identical to those commonly implemented in GIS software and applies Dijkstra's algorithm with diagonal connectivity between cells [Etherington2016]_.


Parallelisation
---------------

**Dijkstra’s algorithm** is a graph search algorithm that solves single-source shortest path for a graph with non-negative weights. Such an algorithm can be quite long to solve especially in **bioLEC** as it needs to be used to compute the **least-cost paths** for every points on the surface.

.. image:: ../RADWave/Notebooks/images/parallel.jpg
   :scale: 50 %
   :alt: Parallel runtime
   :align: center

Here we do not perform a parallelisation of the **Dijkstra’s algorithm** but instead we adopt a simpler strategy where the **Dijkstra trees** for all paths are balanced and distributed over multiple processors using message passing interface (**MPI**). The approach consists in splitting the computational domain row-wise as shown in the above figure.  **Least-cost paths** are then computed for the points belonging to each sub-domain using the **Dijkstra’s algorithm** over the entire region.

.. note::
  Using this approach, LEC computation is significantly reduced and **scales really well with increasing CPUs**.

.. [Bertuzzo2016] E. Bertuzzo, F. Carrara, L. Mari, F. Altermatt, I. Rodriguez-Iturbe & A. Rinaldo -
  Geomorphic controls on species richness. PNAS, 113(7) 1737-1742, `DOI: 10.1073/pnas.1518922113`_, 2016.

.. [Dijkstra1959] E.W. Dijkstra -
  A note on two problems in connexion with graphs. Numer. Math. 1, 269-271, `DOI: 10.1007/BF01386390`_, 1959.

.. [Etherington2016] T.R. Etherington -
  Least-cost modelling and landscape ecology: concepts, applications, and opportunities. Current Landscape Ecology Reports 1:40-53, `DOI: 10.1007/s40823-016-0006-9`_, 2016.

.. [Etherington2017] T.R. Etherington -
  Least-cost modelling with Python using scikit-image, Blog_, 2017.

.. [Lomolino2008] M.V. Lomolino -
  Elevation gradients of species-density: historical and prospective views. Glob. Ecol. Biogeogr. 10, 3-13, `DOI: 10.1046/j.1466-822x.2001.00229.x`_, 2008.


.. [Chelton2001] Chelton, D.B., Ries, J.C., Haines, B.J., Fu, L.L. & Callahan, P.S. -
    Satellite Altimetry, Satellite altimetry and Earth sciences in L.L. Fu and A. Cazenave Ed., Academic Press, 2001

.. [Ribal2019] Ribal, A. & Young, I. R. -
    33 years of globally calibrated wave height and wind speed data based on altimeter observations. **Scientific Data** 6(77), p.100, 2019.


.. _`DOI: 10.1073/pnas.1518922113`: http://www.pnas.org/cgi/doi/10.1073/pnas.1518922113
.. _`DOI: 10.1007/BF01386390`: https://link.springer.com/article/10.1007/BF01386390
.. _`DOI: 10.1007/s40823-016-0006-9`: https://link.springer.com/article/10.1007/s40823-016-0006-9
.. _Blog: http://tretherington.blogspot.com/2017/01/least-cost-modelling-with-python-using.html
.. _`DOI: 10.1046/j.1466-822x.2001.00229.x`: https://doi.org/10.1046/j.1466-822x.2001.00229.x
.. _`PeerJ 2:e453`: https://peerj.com/articles/453/
.. _`scikit-image`: http://scikit-image.org/
.. _`Dijkstra's algorithm`: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
