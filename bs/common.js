/*
通用函数
 */

function btn_disabled (id) {
    let btn = $("#"+id);
    btn.attr("disabled", true);
    btn.css({'background-color': 'gray'});
}

function btn_enabled(id) {
    let btn = $("#"+id);
    btn.attr("disabled", false);
    btn.css({'background-color': 'rgb(30,160,255)'});
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

let option_demo = {
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
        boundaryGap: [0, '100%'],
        splitLine: {
            show: false
        },
        scale: true,
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
            }
        };
        option.series.push(ser);
    }
    if (option.series[0].data.length !== 0) {
        fig.setOption(option);
    }
}

// 添加标注点
function addmarkPoint (params, fig) {
    // console.log(params);
    if (params.componentType !== 'series') return;
    let [x, y] = params.value;
    let op = fig.getOption();
    // console.log(op);
    let markPointData = op.series[params.seriesIndex].markPoint.data;
    markPointData.push({
        name: `x:${x}\ny:${y}`,
        coord: params.value,
        label: {
            show: true,
            formatter: `x:${x}\ny:${y}`,
            position: 'top'
        },
        symbolSize: 4,
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
function deletemarkPoint (params, fig) {
    // console.log(params);
    if (params.componentType !== 'markPoint') return;
    let op = fig.getOption();
    // console.log(op);
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
                    ,area: ['37.5%', '70%']
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

function draw(btn1, btn2, fig_side, low_cutoff_id, high_cutoff_id, farm_name, sn, criterion, data, params) {
    document.getElementById(fig_side).style.display='';
    let sampling_time = data[criterion][params.seriesName]['time'][params.dataIndex];
    let dataset = {'farm_name': farm_name,
        'wind_turbine_name': params.seriesName,
        'point': sn[0]['name'],
        'sampling_time': sampling_time,
    };
    let id1 = btn1;
    // 激活按钮
    btn_enabled(id1);
    let id2 = btn2;
    let lc = $('#'+low_cutoff_id);
    let hc = $('#'+high_cutoff_id);
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

