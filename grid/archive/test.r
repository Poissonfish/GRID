required_pkg = c("MASS", "LDheatmap", "genetics", "EMMREML", "biganalytics",
                "ape", "bigmemory", "gplots", "compiler", "scatterplot3d",
                "R.utils", "data.table", "magrittr", "ggplot2", "rrBLUP", "BGLR")
missing_pkg = required_pkg[!(required_pkg %in% installed.packages()[,"Package"])]
if(length(missing_pkg)) 
    install.packages(missing_pkg, repos="http://cran.rstudio.com/")

tryCatch({
    # for R 3.5 and above
    if (!requireNamespace("BiocManager", quietly = TRUE))
        install.packages("BiocManager")
    BiocManager::install("multtest")
    BiocManager::install("snpStats")
}, error = function(e) {
    # for earlier version of R (< 3.5)
    source("http://www.bioconductor.org/biocLite.R")
	biocLite("multtest")
	biocLite("snpStats")
})
