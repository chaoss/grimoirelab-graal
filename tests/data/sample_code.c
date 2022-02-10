/* 
 * Example file based on BSD-licensed c2rust project example files:
 * https://github.com/immunant/c2rust/blob/master/examples/qsort/qsort.c 
 */

#ifdef DOES_NOT_EXIST
#define DOES_EXIST
#endif

#include <stdio.h>
#include <stdlib.h>

static const unsigned int testvar=0;

void swap(int* a, int* b)
{
    int t = *a;
    *a = *b;
    *b = t;
}

int partition (int arr[], int low, int high)
{
    int pivot = arr[high];
    int i = low - 1;

    for (int j = low; j <= high - 1; j++) {
        if (arr[j] <= pivot) {
            i++;
            swap(&arr[i], &arr[j]);
        }
    }
    swap(&arr[i + 1], &arr[high]);
    return i + 1;
}

void quickSort(int arr[], int low, int high)
{
    if (low < high) {
        int i = partition(arr, low, high);
        quickSort(arr, low, i - 1);
        quickSort(arr, i + 1, high);
    }
}
