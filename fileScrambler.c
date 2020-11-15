#include <stdio.h>
#include <string.h>
#include <stdlib.h>

/*
 * Binary File scrambler
 * by 0fabris
 *
 * Category: Utilities
 * 11/2020
 */

int main(int argc, char **argv){
	
	//Declarations
	FILE *fpr, *fpw;
	char *fname = argv[1];

	//error on parameters
	if(argc < 3){
		printf("usage: %s nf.bin (s-d) [nfdest.bin]\n(s-d) = scramble - descramble\nnfdest.bin = optional destination filename\n", argv[0]); // s = scramble, d = descramble
		return 0;
	}
	
	
	fpr = fopen(fname,"rb");
	fseek(fpr,0,SEEK_END); // go to the end of file
	//Save length
	long endPos = ftell(fpr);
	fseek(fpr,0,SEEK_SET);
	printf("open read file\n");

	//Save destination filename
	char* fwname;
	
	if(argc>3)
		fwname = argv[3];
	else
	{
		fwname = malloc(strlen(fname)+1);
		fwname[0] = 's';
		strcat(fwname,fname);
	}
	
	//save scramble or descramble
	char type;
	if(argc > 2 && (*argv[2] == 's' || *argv[2] == 'd'))
	{
		type = *argv[2];
	}
	else{
		type = 's';
	}

	//Open write file
	fpw = fopen(fwname,"w");
	printf("open write file\n");

	int posCounter = 0;
	char c;
	
	//Scramble or descramble?
	if(type == 's'){
		printf("scrambling...\n");
		//One char from top, and one from bottom
		while(posCounter < (endPos/2))
		{
			//%2 == 0
			fseek(fpr,posCounter,SEEK_SET);
			c = fgetc(fpr);
			fputc(c,fpw);
			//%2 == 1
			fseek(fpr,-1*(posCounter+1),SEEK_END);
			c = fgetc(fpr);
			
			fputc(c,fpw);
			posCounter++;
		}
		//If odd length read single char
		if(posCounter+1 == ftell(fpr)-1)
		{
			fseek(fpr,posCounter,SEEK_SET);
			c = fgetc(fpr);
			fputc(c,fpw);
		}
	}
	else
	{
		printf("descrambling...\n");
		int bCount = 0;
		char buffer[(endPos/2) + 1];
		while(posCounter < endPos){
			fseek(fpr,posCounter,SEEK_SET);
			c = fgetc(fpr);
			if(posCounter%2==0)
				fputc(c,fpw);
			else
				buffer[bCount++] = c; //Add to buffer bottom characters
			posCounter++;
		}
		for(int i = bCount-1; i >=0; i--)
			fputc(buffer[i],fpw); //Reverse buffer and add to file
	}

	//Close handlers
	fclose(fpr);
	fclose(fpw);
	
	printf("ok\n");
	return 0;
}
