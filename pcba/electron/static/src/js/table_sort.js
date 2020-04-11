 function sortTable(sTableId, iCol, sDataType){
          var oTable = document.getElementById(sTableId);
          var oTBody = oTable.tBodies[0];
          var colRows = oTBody.rows;
          var aTRs = new Array();
          for(var i = 0; i < colRows .length; i++){ 
               aTRs[i] = colRows[i];
          } 
          if(oTable.sortCol == iCol){ 
               aTRs.reverse();
          }else{ 
               aTRs.sort(getSortFunction(iCol, sDataType));
          } 
          var oFragement = document.createDocumentFragment();
          for(var i = 0; i < aTRs.length; i++){ 
               oFragement.appendChild(aTRs[i]);
          } 
          oTBody.appendChild(oFragement);
          oTable.sortCol = iCol;
    } 


    function getSortFunction(iCol, sDataType){ 
        return function compareTRs(oTR1, oTR2){ 
           var vValue1, vValue2; 
           if(oTR1.cells[iCol].getAttribute("value")){ 
                vValue1 = convert(oTR1.cells[iCol].getAttribute("value"), sDataType); 
                vValue2 = convert(oTR2.cells[iCol].getAttribute("value"), sDataType); 
           }else{ 
                vValue1 = convert(oTR1.cells[iCol].firstChild.nodeValue, sDataType) 
                vValue2 = convert(oTR2.cells[iCol].firstChild.nodeValue, sDataType) 
           } 
           if(vValue1 < vValue2){ 
                return -1; 
           }else if(vValue1 > vValue2){ 
                return 1; 
           }else{ 
                return 0; 
           } 
        } 
    } 
    function convert(sValue, sDataType){ 
        switch(sDataType){ 
              case "int": 
                 return parseInt(sValue); 
              case "float": 
                 return parseFloat(sValue); 
              case "date": 
                 return new Date(Date.parse(sValue)); 
              default: 
                 return sValue; 
        } 
    } 