(function($){
    $.fn.extend({
        "makeSortable":function(){
            var table=$(this),
                headers=table.find('th');
            for(var i=0,len=headers.length;i<len;i++){
                (function(n){
                    var flag=false;
                    headers.eq(n).click(function() {
                        var tbody=table.children('tbody').eq(0);
                        var rows=tbody.children('tr');
                        rows=Array.prototype.slice.call(rows,0);

                        rows.sort(function(row1,row2){
                            var val1=$(row1).children('td').eq(n).text();
                            var val2=$(row2).children('td').eq(n).text();
                            if(val1>val2){
                                return 1;
                            }else if(val1<val2){
                                return -1;
                            }else{
                                return 0;
                            }
                        });

                        if(flag){
                            rows.reverse();
                        }

                        tbody.append(rows);
                        flag=!flag;
                    });
                }(i));
            }

            return this;
        }
    });
})(jQuery);

$(function(){
    $("#table2xx").makeSortable();
});
