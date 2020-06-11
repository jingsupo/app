/*
通用函数
 */

function getDate() {
    let date = new Date();
    let Months = date.getMonth() + 1<10 ? '0' + (date.getMonth() + 1):date.getMonth() + 1; //月份从0开始，因此要+1
    let Dates = date.getDate()<10 ? '0' + date.getDate():date.getDate();
    let Hours = date.getHours()<10 ? '0' + date.getHours():date.getHours();
    let Minutes = date.getMinutes()<10 ? '0' + date.getMinutes():date.getMinutes();
    let Seconds = date.getSeconds()<10 ? '0' + date.getSeconds():date.getSeconds();

    return date.getFullYear() + Months + Dates + Hours + Minutes + Seconds;
}

function btn_disabled (id) {
    let btn = $("#"+id);
    btn.attr("disabled", true);
    btn.css({'background-color': 'gray'});
}

function btn_enabled (id) {
    let btn = $("#"+id);
    btn.attr("disabled", false);
    btn.css({'background-color': 'rgb(30,160,255)'});
}

function preventDefault(elementID) {
    // addEventListener() 方法用于向指定元素添加事件句柄
    document.getElementById(elementID).addEventListener('contextmenu', function (e) {
        // event.preventDefault() 方法阻止元素发生默认的行为
        e.preventDefault();
    }, false);
}

// 多窗口弹层
function draw_iframe (content, title, id, flag, data, params) {
    layui.use('layer', function () {
        let $ = layui.jquery, layer = layui.layer;

        //触发事件
        let active = {
            setTop: function(){
                let that = this;
                //多窗口模式，层叠置顶
                layer.open({
                    type: 2 //iframe
                    ,title: title
                    ,area: ['40%', '80%']
                    ,shade: 0
                    ,maxmin: true
                    ,offset: []
                    ,content: content
                    ,btn: ['全部关闭']
                    ,yes: function(){
                        layer.closeAll();
                    }
                    ,zIndex: layer.zIndex //重点1
                    ,success: function(layero, index){
                        layer.setTop(layero); //重点2
                        //拿到iframe元素
                        let iframe = window['layui-layer-iframe' + index];
                        //调用子页面的全局函数
                        iframe.child(flag, data, params);
                    }
                });
            }
        };

        // 解决JQuery中click里面包含click事件，出现重复执行的问题
        $("#"+id).unbind('click').on('click', function(){
            let othis = $(this), method = othis.data('method');
            active[method] ? active[method].call(this, othis) : '';
            // 只允许点击一次按钮
            btn_disabled(id);
        });
    });
}

// 趋势图详细分析
function draw(farm_name, point_name, criterion, data, params) {
    if ($('#point-detail').prop('checked')) {
        layui.use('layer', function () {
            let layer = layui.layer;

            layer.open({
                type: 1
                ,title: '详细分析'
                ,shade: 0
                ,area: ['200px', '250px']
                ,id: 'trend_layer'  //设置该值后，不管是什么类型的层，都只允许同时弹出一个。
                ,resize: false
                ,offset: 'r'
                ,content: '<button data-method="setTop" class="layui-btn" id="btn-tf">时域频域图</button><br /><label for="lc">低</label><input type="text" class="cutoff" id="lc" placeholder="请输入低截止频率"><br /><label for="hc">高</label><input type="text" class="cutoff" id="hc" placeholder="请输入高截止频率"><br /><br /><button data-method="setTop" class="layui-btn" id="btn-env">包络图</button>'
            });
        });
        let sampling_time = data[criterion][params.seriesName]['time'][params.dataIndex];
        let dataset = {'farm_name': farm_name,
            'wind_turbine_name': params.seriesName,
            'point': point_name,
            'sampling_time': sampling_time,
        };
        let id1 = 'btn-tf';
        // 激活按钮
        btn_enabled(id1);
        let id2 = 'btn-env';
        let lc = $('#lc');
        let hc = $('#hc');
        let low_cutoff = lc.val();
        let high_cutoff = hc.val();
        if (low_cutoff !== '' && high_cutoff !== '') {
            // 激活按钮
            btn_enabled(id2);
        }
        else {
            // 禁用按钮
            btn_disabled(id2);
        }
        if (low_cutoff !== '') {
            dataset['low_cutoff'] = low_cutoff;
        }
        if (high_cutoff !== '') {
            dataset['high_cutoff'] = high_cutoff;
        }
        lc.bind('input propertychange', function() {
            if (lc.val() !== '' && hc.val() !== '') {
                btn_enabled(id2);
            }
            else {
                btn_disabled(id2);
            }
            low_cutoff = lc.val();
            dataset['low_cutoff'] = low_cutoff;
        });
        hc.bind('input propertychange', function() {
            if (lc.val() !== '' && hc.val() !== '') {
                btn_enabled(id2);
            }
            else {
                btn_disabled(id2);
            }
            high_cutoff = hc.val();
            dataset['high_cutoff'] = high_cutoff;
        });
        draw_iframe('/draw', '时域频域图', id1, 1, dataset, params);
        draw_iframe('/draw', '包络图', id2, 2, dataset, params);
    }
}

// iframe弹层
function iframe (content, title, data) {
    layui.use('layer', function () {
        let layer = layui.layer;

        layer.open({
            type: 2 //iframe
            ,title: title
            ,area: ['40%', '80%']
            ,id: 'iframe_layer'  //设置该值后，不管是什么类型的层，都只允许同时弹出一个。
            ,shade: 0
            ,maxmin: true
            ,offset: []
            ,content: content
            ,success: function(layero, index){
                //拿到iframe元素
                let iframe = window['layui-layer-iframe' + index];
                //调用子页面的全局函数
                iframe.child(data);
            }
        });
    });
}

function msg (text) {
    layui.use('layer', function () {
        let layer = layui.layer;

        layer.msg(text);
    });
}

function loading () {
    layui.use('layer', function () {
        //加载层
        let index = layer.load(0, {shade: false}); //0代表加载的风格，支持0-2
    });
}

// 导出ECharts图表图片，返回一个 base64 的 URL
function getDataURL (fig) {
    return fig.getDataURL({
        pixelRatio: 2,
        backgroundColor: '#fff'
    });
}

option_demo = {
    color: ['blue', '#00B83F', 'red', '#FF7F00', '#FF00FF', '#A020F0'],
    title: {
        text: ''
    },
    tooltip: {
        trigger: 'axis',
        triggerOn: 'mousemove|click',
    },
    legend: {
        top: '6%',
        data: [],
    },
    xAxis: {
        type: 'time',
        name: '',
        nameLocation: 'center',
        nameGap: 35,
        max: 'dataMax',
        splitLine: {
            show: false
        },
        splitNumber: 10,
        // scale: true,
    },
    yAxis: {
        type: 'value',
        name: '',
        nameLocation: 'center',
        nameGap: 35,
        max: function(value) {
            if (value.max > 1) {
                return value.max;
            }
            else {
                return 1;
            }
        },
        boundaryGap: [0, '100%'],
        splitLine: {
            show: false
        },
        // scale: true,
    },
    series: [],
    // dataZoom: [{
    //     //
    // }],
    toolbox: { // 工具栏
        feature: {
            dataZoom: { // 框选缩放功能
                show: true, // show为true时，才能触发takeGlobalCursor事件
                yAxisIndex: 'none',
            },
            restore: {
                show: true
            },
            saveAsImage: {
                show: true,
                type: 'png',
            },
        }
    }
};

function setOption_tfe (fig, option, title_text, value, data, wind_turbine_selected) {
    // JSON对象复制-深拷贝
    option = JSON.parse(JSON.stringify(option_demo));
    option.title.text = title_text;
    option.xAxis.type = 'value';
    for (let c in wind_turbine_selected) {
        if (!wind_turbine_selected.hasOwnProperty(c)) continue;
        option.legend.data.push(wind_turbine_selected[c]);
        let ser = {
            name: wind_turbine_selected[c],
            type: 'line',
            lineStyle: {
                width: 1
            },
            showSymbol: false,
            hoverAnimation: true,
            data: data[value],
            markPoint: {
                data: [],
            }
        };
        option.series.push(ser);
    }
    if (option.series[0].data.length !== 0) {
        fig.setOption(option);
    }
}

function setOption_trend (fig, option, title_text, xAxis_name, yAxis_name, criterion, value, data, wind_turbine_selected) {
    // JSON对象复制-深拷贝
    option = JSON.parse(JSON.stringify(option_demo));
    option.title.text = title_text;
    option.xAxis.name = xAxis_name;
    option.yAxis.name = yAxis_name;
    for (let c in wind_turbine_selected) {
        if (!wind_turbine_selected.hasOwnProperty(c)) continue;
        option.legend.data.push(wind_turbine_selected[c]);
        let ser = {
            name: wind_turbine_selected[c],
            type: 'line',
            lineStyle: {
                width: 1
            },
            showSymbol: false,
            // type: 'scatter',
            // symbolSize: 6,
            hoverAnimation: true,
            data: data[criterion][wind_turbine_selected[c]][value],
            markPoint: {
                data: [],
            },
            markLine: {
                data: [],
            },
        };
        option.series.push(ser);
    }
    if (option.series[0].data.length !== 0) {
        fig.setOption(option);
    }
}

// 标注点
function markPoint(fig, params) {
    if ($('#mark-point').prop('checked')) {
        addmarkPoint (fig, params);
    }
}

// 批量删除标注点
function markPoint_batch_deletion (fig) {
    $('#del-mp').click(function () {
        fig.setOption({
            series: [{
                markPoint: {
                    data: []
                }
            }]
        });
    });
}

// 添加标注点
function addmarkPoint (fig, params) {
    if (params.componentType !== 'series') return;
    let [x, y] = params.value;
    let op = fig.getOption();
    let markPointData = op.series[params.seriesIndex].markPoint.data;
    markPointData.push({
        name: `x:${x}\ny:${y}`,
        coord: params.value,
        label: {
            show: true,
            formatter: `x:${x}\ny:${y}`,
            position: 'top'
        },
        symbolSize: 6,
        symbol: 'rect',
        itemStyle: {
            color: '#000'
        }
    });
    let series = op.series;
    series[params.seriesIndex] = {
        markPoint: {
            data: markPointData
        }
    };
    fig.setOption({
        series: series
    });
}

// 删除标注点
function deletemarkPoint (fig, params) {
    if (params.componentType !== 'markPoint') return;
    let op = fig.getOption();
    let markPointData = op.series[params.seriesIndex].markPoint.data;
    let newMarkPointData = markPointData.filter(({ name }) => name !== params.name);
    let series = op.series;
    series[params.seriesIndex] = {
        markPoint: {
            data: newMarkPointData
        }
    };
    fig.setOption({
        series: series
    });
}

// 倍频
function freqMulti(fig, params) {
    let markLineData = [];
    for (let i = 1; i < 6; i++) {
        markLineData.push({
            lineStyle: {
                color: 'red',
                width: 2,
                type: 'solid'
            },
            name: i.toString() + 'X',
            xAxis: i * params.value[0]
        });
    }
    if ($('#freq-multi').prop('checked')) {
        fig.setOption({
            series: [{
                markLine: {
                    silent: true,
                    symbol: 'none',
                    label: {
                        formatter: '{b}'
                    },
                    data: markLineData
                }
            }]
        });
    }
}

// 批量删除倍频
function freqMulti_batch_deletion (fig) {
    $('#del-fm').click(function () {
        fig.setOption({
            series: [{
                markLine: {
                    data: []
                }
            }]
        });
    });
}

