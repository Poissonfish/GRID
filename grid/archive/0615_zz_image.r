############ ############ ############
# Date: Jun 15, 2020 
# Author: Chunpeng James Chen
# Description: 
#   It's a code showing how to load an image into a r-compatible data.frame
############ ############ ############
 
# DEPENDENCIES  
############ ############ ############

# install.packages("imager")
library(imager)

# FUNCTIONS 
############ ############ ############

# Description
#   convert imager object to data.frame (cols: x, y, c1, c2...)
# Input
#   image: image object loaded from library imager
# Output
#   df: a data.frame containing information of xy coordinates and channel values
img2df <- function(image) {
    w <- dim(image)[1]
    h <- dim(image)[2]
    d <- 3
    df <- matrix(image[,, 1, 1:d], nrow=h * w, ncol=d) %>%
                    data.frame(x=rep(1 : w, length=w * h),
                               y=rep(1 : h, each=w),.)
    names(df) <- c("x", "y", paste0("c", 1:d))
    return (df)
}

# Description
#   convert an image file to data.frame
# Input
#   filename: file path to where the file is stored 
# Output
#   df: a data.frame containing information of xy coordinates and channel values
file2df <- function(filename) {
    filename %>%
        load.image() %>% 
        img2df() %>% 
        return()
}

# Description
#   convert a data.frame (col: x, y, c1, c2 ...) to a imager object
# Input
#   df: a dataframe containing information of xy coordinates and channel values
# Output
#   img: a imagery object which is ready to be ploted
df2img <- function(df) {
    w = max(df$x)
    h = max(df$y)
    d = ncol(df) - 2
    subset(df, select=-c(x, y)) %>% 
        as.matrix() %>% 
        as.vector() %>% 
        as.cimg(dim=c(w, h, 1, d)) %>% 
        return()
}

# Description
#   save an imager object as an image file
# Input
#   image: imager object or 2d matrix (single channel image)
#   filename: a path where the image will be saved
# Output
#   NA
img2file <- function(image, filename) {
    cimg <- as.cimg(image)
    save.image(cimg, filename)
}

# SAMPLE CODE
############ ############ ############
# specify file name
filename <- "test.png"

# get data.frame from a file (xy coordinates + 3 channels)
# OPTION 1
img <- load.image(filename)
df <- img2df(img)
# OPTION 2
df <- file2df(filename)

# get PCA data.frame (xy coordinates + PCs)
mat_pc <- prcomp(df[, 3 : (3 + 2)], scale=T, center=T)$x 
df_pc <- data.frame(df[, c("x", "y")], mat_pc)

# get PCA image
img_pc <- df2img(df_pc)

# plot original image
plot(img)

# plot index: (c1 - c2) / (c1 + c2)
c1 = img[,, 1]
c2 = img[,, 2]
img_index = (c1 - c2) / (c1 + c2)
heatmap(img_index, Rowv=NA, Colv=NA)

# plot all 3 PCs
plot(img_pc)

# plot the 2nd PC
heatmap(img_pc[, , 2], Rowv=NA, Colv=NA)

# plot (pc1-pc2)/(pc1+pc2)
pc1 = img_pc[, , 1]
pc2 = img_pc[, , 2]
img_index_pc = (pc1 - pc2) / (pc1 + pc2)
heatmap(img_index_pc, Rowv=NA, Colv=NA)

# save images
img2file(img_index, "index.png")
img2file(img_pc, "pc.png")
img2file(img_pc[,, 2], "pc2.png")
