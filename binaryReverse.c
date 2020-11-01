#include <stdio.h>
#include <string.h>
#include <stdlib.h>

/*
 * Binary File reverser
 * by 0fabris
 *
 * Category: Utilities
 * 10/2020
 */

int main(int argc, char **argv){
	
	//Declarations
	FILE *fpr, *fpw;
	char *fname = argv[1];

	//error on parameters
	if(argc < 2){
		printf("usage: %s nf.bin [nfdest.bin]", argv[0]);
		return 0;
	}
	
	
	fpr = fopen(fname,"rb");
	fseek(fpr,0,SEEK_END); // go to the end of file
	printf("open read file\n");

	char* fwname;
	
	if(argc>2)
		fwname = argv[2];
	else
	{
		fwname = malloc(strlen(fname)+1);
		fwname[0] = 'r';
		strcat(fwname,fname);
	}


	fpw = fopen(fwname,"w");
	printf("open write file\n");

	//read and go back until start of file
	while(ftell(fpr) > 0){
		fseek(fpr,-1,SEEK_CUR);
		fputc(fgetc(fpr),fpw);
		fseek(fpr,-1,SEEK_CUR);
	}

	//Close handlers
	fclose(fpr);
	fclose(fpw);
	
	printf("ok\n");
	return 0;
}
