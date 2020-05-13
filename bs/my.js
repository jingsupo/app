// 配置加载模块
require.config({
    paths: {
        "underscore": "static/js/underscore-min",
    }
});
require(['underscore'], function () {
    //
});

// 加载日期与时间组件
layui.use(['laydate'], function() {
    let laydate = layui.laydate;

    laydate.render({
        elem: '#from_time',
        type: 'datetime',
        format: 'yyyyMMddHHmmss'
    });

    laydate.render({
        elem: '#to_time',
        type: 'datetime',
        format: 'yyyyMMddHHmmss'
    });

    laydate.render({
        elem: '#from_time2',
        type: 'datetime',
        format: 'yyyyMMddHHmmss'
    });

    laydate.render({
        elem: '#to_time2',
        type: 'datetime',
        format: 'yyyyMMddHHmmss'
    });
});

$(document).ready(function () {
    // 初始化隐藏ztree插件
    document.getElementById('treeDemo').style.display='none';
    // 初始化隐藏loading容器
    document.getElementById('loading-image').style.display='none';
    $.ajax({
        url: "/get_db_names",
        type: "POST",
        dataType: "json",
        success: function (data) {
            let farm = document.getElementById('farm');
            for (let i=0; i < data.length; i++) {
                farm.options.add(new Option(data[i], i+1));
            }
        }
    });
    let date = new Date();
    let Months = date.getMonth() + 1<10 ? '0' + (date.getMonth() + 1):date.getMonth() + 1; //月份从0开始，因此要+1
    let Dates = date.getDate()<10 ? '0' + date.getDate():date.getDate();
    let Hours = date.getHours()<10 ? '0' + date.getHours():date.getHours();
    let Minutes = date.getMinutes()<10 ? '0' + date.getMinutes():date.getMinutes();
    let Seconds = date.getSeconds()<10 ? '0' + date.getSeconds():date.getSeconds();
    let now = date.getFullYear() + Months + Dates + Hours + Minutes + Seconds;
    let from_time = now - 600000000;
    // 设置默认时间
    $('#from_time').val(from_time);
    $('#from_time2').val(from_time);
    $('#to_time').val(now);
    $('#to_time2').val(now);
    // addEventListener() 方法用于向指定元素添加事件句柄
    document.getElementById("fig1").addEventListener('contextmenu', function (e) {
        // event.preventDefault() 方法阻止元素发生默认的行为
        e.preventDefault();
    }, false);
    // addEventListener() 方法用于向指定元素添加事件句柄
    document.getElementById("fig2").addEventListener('contextmenu', function (e) {
        // event.preventDefault() 方法阻止元素发生默认的行为
        e.preventDefault();
    }, false);
    // addEventListener() 方法用于向指定元素添加事件句柄
    document.getElementById("fig3").addEventListener('contextmenu', function (e) {
        // event.preventDefault() 方法阻止元素发生默认的行为
        e.preventDefault();
    }, false);
});

$(document).ready(function () {
    // 必须使用#id进行选择才有效果
    $('#farm').change(function () {
        let treeObj = $.fn.zTree.getZTreeObj("treeDemo");
        if (treeObj) {
            treeObj.destroy()
        }
        let farm_name = $('#farm').find('option:selected').text();
        $.ajax({
            url: "/farm",
            type: "POST",
            data: {'farm_name': farm_name},
            dataType: "json",
            success: function (data) {
                let wind_turbine = document.getElementById('wind_turbine');
                // 默认清空已经存在的项目
                wind_turbine.options.length = 1;
                for (let i=0; i < data.length; i++) {
                    wind_turbine.options.add(new Option(data[i], i+1));
                }
                // 默认使序号为1的项目选中
                wind_turbine.options[1].selected = true;
            }
        });
    });
});

$(document).ready(function () {
    $("input[name=q]").click(function () {
        let farm_name = $('#farm').find('option:selected').text();
        let wind_turbine_name = $('#wind_turbine').find('option:selected').text();
        let from_time = $('#from_time').val();
        let to_time = $('#to_time').val();
        let from_rotate_speed = $('#from_rotate_speed').find('option:selected').text();
        let to_rotate_speed = $('#to_rotate_speed').find('option:selected').text();
        if (farm_name === '选择风场' || wind_turbine_name === '选择风机') {
            alert('请先选择相应项目！');
        }
        else {
            let dataset = {'farm_name': farm_name,
                'wind_turbine_name': wind_turbine_name,
                'from_time': from_time,
                'to_time': to_time,
                'from_rotate_speed': from_rotate_speed,
                'to_rotate_speed': to_rotate_speed,
            };
            $.ajax({
                url: "/q",
                type: "POST",
                data: dataset,
                dataType: "json",
                success: function (data) {
                    let zTreeObj;
                    let setting = {
                        callback: {
                            onClick: zTreeOnClick
                        },
                        view: {
                            showLine: false
                        }
                    };
                    let zNodes = [];
                    let child = [];
                    for (let key in data['point_description']) {
                        child.push({name:data['point_description'][key]});
                    }
                    for (let i=0; i < data['sampling_time'].length; i++) {
                        zNodes.push({name:data['sampling_time'][i], open:false, children:child})
                    }
                    function zTreeOnClick(event, treeId, treeNode) {
                        // console.log(treeNode.tId + ", " + treeNode.name);
                        let treeObj = $.fn.zTree.getZTreeObj("treeDemo");
                        // 当前选中节点
                        let sn = treeObj.getSelectedNodes();
                        let html;
                        if (sn[0].hasOwnProperty('children') && sn[0].children.length > 0) {
                            html = data['rotate_speed'][sn[0].name];
                        }
                        else {
                            // 选中节点的父节点
                            let pn = sn[0].getParentNode();
                            html = data['rotate_speed'][pn.name];
                        }
                        document.getElementById('time_info').innerHTML = '转速：' + html;
                        // 显示time_info容器
                        document.getElementById('time_info').style.display='';
                    }
                    $(document).ready(function(){
                        zTreeObj = $.fn.zTree.init($("#treeDemo"), setting, zNodes);
                    });
                }
            });
            // 显示ztree插件
            document.getElementById('treeDemo').style.display='';
        }
    });
});

let option_tfe = {
    title: {
        text: ''
    },
    tooltip: {
        trigger: 'axis',
        triggerOn: 'mousemove|click',
    },
    xAxis: {
        type: 'value',
        splitLine: {
            show: false
        }
    },
    yAxis: {
        type: 'value',
        boundaryGap: [0, '100%'],
        splitLine: {
            show: false
        }
    },
    series: [{
        name: '',
        type: 'line',
        lineStyle: {
            width: 1
        },
        showSymbol: false,
        hoverAnimation: true,
        data: [],
        markPoint: {
            data: [],
        }
    }],
    dataZoom: [{
        //
    }],
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

$(document).ready(function () {
    $("input[name=tf]").click(function () {
        if (fig1.dispose) {
            fig1.dispose();
        }
        fig1 = echarts.init(document.getElementById('fig1'), 'white', {renderer: 'canvas'});
        if (fig2.dispose) {
            fig2.dispose();
        }
        fig2 = echarts.init(document.getElementById('fig2'), 'white', {renderer: 'canvas'});
        if (fig3.dispose && fig3.getOption() !== undefined) {
            if (isInArray(['envelope'], fig3.getOption().series[0].data[0].name)) {
                // 如果当前画布上不是包络图，则销毁实例
                fig3.dispose();
            }
        }
        if (fig4.dispose) {
            fig4.dispose();
        }
        let farm_name = $('#farm').find('option:selected').text();
        let wind_turbine_name = $('#wind_turbine').find('option:selected').text();
        let treeObj = $.fn.zTree.getZTreeObj("treeDemo");
        if (farm_name === '选择风场' || wind_turbine_name === '选择风机' || treeObj == null) {
            alert('请先选择左侧项目！');
        }
        else {
            // 当前选中节点
            let sn = treeObj.getSelectedNodes();
            if (sn.length === 0) {
                alert('请选择测点！');
            }
            else if (sn[0].hasOwnProperty('children') && sn[0].children.length > 0) {
                alert('请选择子节点！');
            }
            else {
                // 选中节点的父节点
                let pn = sn[0].getParentNode();
                let dataset = {'farm_name': farm_name,
                    'wind_turbine_name': wind_turbine_name,
                    'sampling_time': pn['name'],
                    'point': sn[0]['name'],
                };
                $.ajax({
                    url: "/tf",
                    type: "POST",
                    data: dataset,
                    dataType: "json",
                    beforeSend: function () {
                        document.getElementById('loading-image').style.display='';
                    },
                    complete: function () {
                        // $('#loading-image').remove();
                        document.getElementById('loading-image').style.display='none';
                    },
                    success: function (data) {
                        // JSON对象复制-深拷贝
                        let option_ts = JSON.parse(JSON.stringify(option_tfe));
                        option_ts.title.text = '时域图';
                        option_ts.series[0].name = '振动信号';
                        option_ts.series[0].data = data['time_series'];
                        fig1.setOption(option_ts);
                        // 增加自定义参数而不覆盖原本的默认参数
                        fig1.on('click', (params) => {
                            addmarkPoint (params, fig1);
                            document.getElementById('time_info').innerHTML = 'fig1';
                        });
                        fig1.on('contextmenu', (params) => { deletemarkPoint (params, fig1) });
                        let option_freq = JSON.parse(JSON.stringify(option_tfe));
                        option_freq.title.text = '频域图';
                        option_freq.series[0].name = '振幅';
                        option_freq.series[0].data = data['freq'];
                        fig2.setOption(option_freq);
                        // 增加自定义参数而不覆盖原本的默认参数
                        fig2.on('click', (params) => {
                            addmarkPoint (params, fig2);
                            document.getElementById('time_info').innerHTML = 'fig2';
                        });
                        fig2.on('contextmenu', (params) => { deletemarkPoint (params, fig2) });
                    }
                });
            }
        }
    });
});

$(document).ready(function () {
    $("input[name=envelope]").click(function () {
        if (fig3.dispose) {
            fig3.dispose();
        }
        fig3 = echarts.init(document.getElementById('fig3'), 'white', {renderer: 'canvas'});
        if (fig1.dispose && fig1.getOption() !== undefined) {
            if (isInArray(['ts', 'freq'], fig1.getOption().series[0].data[0].name)) {
                // 如果当前画布上不是时域图和频域图，则销毁实例
                fig1.dispose();
            }
        }
        if (fig2.dispose && fig2.getOption() !== undefined) {
            if (isInArray(['ts', 'freq'], fig2.getOption().series[0].data[0].name)) {
                // 如果当前画布上不是时域图和频域图，则销毁实例
                fig2.dispose();
            }
        }
        if (fig4.dispose) {
            fig4.dispose();
        }
        let farm_name = $('#farm').find('option:selected').text();
        let wind_turbine_name = $('#wind_turbine').find('option:selected').text();
        let treeObj = $.fn.zTree.getZTreeObj("treeDemo");
        let low_cutoff = $('#low_cutoff').val();
        let high_cutoff = $('#high_cutoff').val();
        if (farm_name === '选择风场' || wind_turbine_name === '选择风机' || treeObj == null) {
            alert('请先选择左侧项目！');
        }
        else {
            // 当前选中节点
            let sn = treeObj.getSelectedNodes();
            if (sn.length === 0) {
                alert('请选择测点！');
            }
            else if (sn[0].hasOwnProperty('children') && sn[0].children.length > 0) {
                alert('请选择子节点！');
            }
            else {
                // 选中节点的父节点
                let pn = sn[0].getParentNode();
                let dataset = {'farm_name': farm_name,
                    'wind_turbine_name': wind_turbine_name,
                    'sampling_time': pn['name'],
                    'point': sn[0]['name'],
                    'low_cutoff': low_cutoff,
                    'high_cutoff': high_cutoff,
                };
                $.ajax({
                    url: "/envelope",
                    type: "POST",
                    data: dataset,
                    dataType: "json",
                    beforeSend: function () {
                        document.getElementById('loading-image').style.display='';
                    },
                    complete: function () {
                        document.getElementById('loading-image').style.display='none';
                    },
                    success: function (data) {
                        let option_envelope = JSON.parse(JSON.stringify(option_tfe));
                        option_envelope.title.text = '包络图';
                        option_envelope.series[0].name = '振幅';
                        option_envelope.series[0].data = data['envelope'];
                        fig3.setOption(option_envelope);
                        // 增加自定义参数而不覆盖原本的默认参数
                        fig3.on('click', (params) => {
                            addmarkPoint (params, fig3);
                            document.getElementById('time_info').innerHTML = 'fig3';
                        });
                        fig3.on('contextmenu', (params) => { deletemarkPoint (params, fig3) });
                    }
                });
            }
        }
    });
});

let option_trend = {
    title: {
        text: ''
    },
    tooltip: {
        trigger: 'axis',
        triggerOn: 'mousemove|click',
    },
    legend: {
        data: []
    },
    xAxis: {
        type: 'time',
        splitLine: {
            show: false
        },
        scale: true,
    },
    yAxis: {
        type: 'value',
        boundaryGap: [0, '100%'],
        splitLine: {
            show: false
        },
        scale: true,
    },
    series: [],
    dataZoom: [{
        //
    }],
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

function setOption_trend (fig, option, title_text, criterion, value, data, wind_turbine_selected) {
    // JSON对象复制-深拷贝
    option = JSON.parse(JSON.stringify(option_trend));
    option.title.text = title_text;
    for (let c in wind_turbine_selected) {
        option.legend.data.push(wind_turbine_selected[c]);
        let ser = {
            name: wind_turbine_selected[c],
            type: 'scatter',
            showSymbol: 6,
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

$(document).ready(function () {
    $("input[name=trend]").click(function () {
        if (fig1.dispose) {
            fig1.dispose();
        }
        fig1 = echarts.init(document.getElementById('fig1'), 'white', {renderer: 'canvas'});
        if (fig2.dispose) {
            fig2.dispose();
        }
        fig2 = echarts.init(document.getElementById('fig2'), 'white', {renderer: 'canvas'});
        if (fig3.dispose) {
            fig3.dispose();
        }
        fig3 = echarts.init(document.getElementById('fig3'), 'white', {renderer: 'canvas'});
        if (fig4.dispose) {
            fig4.dispose();
        }
        fig4 = echarts.init(document.getElementById('fig4'), 'white', {renderer: 'canvas'});
        let criterion = $('#criterion').find('option:selected').val();
        let more_wind_turbine = document.getElementById('more_wind_turbine');
        let wind_turbine_selected = [];
        for (let i = 0; i < more_wind_turbine.length; i++) {
            if (more_wind_turbine.options[i].selected) {
                wind_turbine_selected.push(more_wind_turbine[i].text)
            }
        }
        let farm_name = $('#farm').find('option:selected').text();
        let wind_turbine_name = $('#wind_turbine').find('option:selected').text();
        let from_time = $('#from_time2').val();
        let to_time = $('#to_time2').val();
        let from_rotate_speed = $('#from_rotate_speed2').find('option:selected').text();
        let to_rotate_speed = $('#to_rotate_speed2').find('option:selected').text();
        let treeObj = $.fn.zTree.getZTreeObj("treeDemo");
        if (farm_name === '选择风场' || wind_turbine_name === '选择风机' || treeObj == null) {
            alert('请先选择左侧项目！');
        }
        else {
            // 当前选中节点
            let sn = treeObj.getSelectedNodes();
            if (sn.length === 0) {
                alert('请选择测点！');
            }
            else if (sn[0].hasOwnProperty('children') && sn[0].children.length > 0) {
                alert('请选择子节点！');
            }
            else {
                if (wind_turbine_selected.length === 0) {
                    alert('请选择风机！');
                }
                else {
                    let dataset = {'farm_name': farm_name,
                        'point': sn[0]['name'],
                        'criterion': criterion,
                        'wind_turbine_selected': JSON.stringify(wind_turbine_selected),
                        'from_time': from_time,
                        'to_time': to_time,
                        'from_rotate_speed': from_rotate_speed,
                        'to_rotate_speed': to_rotate_speed,
                    };
                    $.ajax({
                        url: "/trend",
                        type: "POST",
                        data: dataset,
                        dataType: "json",
                        beforeSend: function () {
                            document.getElementById('loading-image').style.display='';
                        },
                        complete: function () {
                            document.getElementById('loading-image').style.display='none';
                        },
                        success: function (data) {
                            if (criterion === '1') {
                                let option_ev = {};
                                setOption_trend(fig1, option_ev, 'ev图', 'vdi', 'ev', data, wind_turbine_selected);
                                // 增加自定义参数而不覆盖原本的默认参数
                                fig1.on('click', (params) => {
                                    addmarkPoint (params, fig1);
                                    let [x, y] = params.value;
                                    let sampling_time = data['vdi'][params.seriesName]['time'][params.dataIndex];
                                    document.getElementById('fig1_side').innerHTML = x+'<br>'+y+'<br>'+'<form action="/2" method="POST" target="_blank"><p>time <input type="text" name="time" value='+sampling_time+'></p ><input type="submit" id="draw"></form>';
                                });
                                fig1.on('contextmenu', (params) => { deletemarkPoint (params, fig1) });

                                let option_ev2 = {};
                                setOption_trend(fig2, option_ev2, 'ev2图', 'vdi', 'ev2', data, wind_turbine_selected);
                                fig2.on('click', (params) => {
                                    addmarkPoint (params, fig2);
                                    document.getElementById('time_info').innerHTML = data['vdi'][params.seriesName]['time'][params.dataIndex];
                                });
                                fig2.on('contextmenu', (params) => { deletemarkPoint (params, fig2) });

                                let option_iv = {};
                                setOption_trend(fig3, option_iv, 'iv图', 'vdi', 'iv', data, wind_turbine_selected);
                                fig3.on('click', (params) => {
                                    addmarkPoint (params, fig3);
                                    document.getElementById('time_info').innerHTML = data['vdi'][params.seriesName]['time'][params.dataIndex];
                                });
                                fig3.on('contextmenu', (params) => { deletemarkPoint (params, fig3) });
                            }
                            if (criterion === '2') {
                                let option_k = {};
                                setOption_trend(fig1, option_k, 'k图', 'dimensionless', 'kurtosisfactor', data, wind_turbine_selected);
                                // 增加自定义参数而不覆盖原本的默认参数
                                fig1.on('click', (params) => {
                                    addmarkPoint (params, fig1);
                                    document.getElementById('time_info').innerHTML = data['dimensionless'][params.seriesName]['time'][params.dataIndex];
                                });
                                fig1.on('contextmenu', (params) => { deletemarkPoint (params, fig1) });

                                let option_p = {};
                                setOption_trend(fig2, option_p, 'p图', 'dimensionless', 'pulsefactor', data, wind_turbine_selected);
                                fig2.on('click', (params) => {
                                    addmarkPoint (params, fig2);
                                    document.getElementById('time_info').innerHTML = data['dimensionless'][params.seriesName]['time'][params.dataIndex];
                                });
                                fig2.on('contextmenu', (params) => { deletemarkPoint (params, fig2) });

                                let option_k2 = {};
                                setOption_trend(fig3, option_k2, 'k2图', 'dimensionless', 'kurtosisfactor2', data, wind_turbine_selected);
                                fig3.on('click', (params) => {
                                    addmarkPoint (params, fig3);
                                    document.getElementById('time_info').innerHTML = data['dimensionless'][params.seriesName]['time'][params.dataIndex];
                                });
                                fig3.on('contextmenu', (params) => { deletemarkPoint (params, fig3) });

                                let option_p2 = {};
                                setOption_trend(fig4, option_p2, 'p2图', 'dimensionless', 'pulsefactor2', data, wind_turbine_selected);
                                fig4.on('click', (params) => {
                                    addmarkPoint (params, fig4);
                                    document.getElementById('time_info').innerHTML = data['dimensionless'][params.seriesName]['time'][params.dataIndex];
                                });
                                fig4.on('contextmenu', (params) => { deletemarkPoint (params, fig4) });
                            }
                        }
                    });
                }

            }
        }
    });
});

$(function () {
    let Btn = $("input[name=spectrum_envelope]");
    let Btn2 = $("input[name=trend_analysis]");
    let Pop = $('#pop');
    let Pop2 = $('#pop2');
    let PopCon = $('.pop_con');

    Btn.click(function () {
        Pop.fadeIn();
        return false;
    });
    Btn2.click(function () {
        let wind_turbine = $('#wind_turbine option');
        let wt = wind_turbine.map(function () {return $(this).text();});
        let more_wind_turbine = document.getElementById('more_wind_turbine');
        // 默认清空已经存在的项目
        $("#more_wind_turbine").empty();
        for (let i=0; i < wt.length; i++) {
            more_wind_turbine.options.add(new Option(wt[i], i+1));
        }
        Pop2.fadeIn();
        return false;
    });
    $(window).click(function () {
        Pop.fadeOut();
        Pop2.fadeOut();
    });
    PopCon.click(function () {
        return false;
    });
    $('#envelope').click(function () {
        Pop.fadeOut();
    });
    $('#trend').click(function () {
        Pop2.fadeOut();
    });
});

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

window.onresize = function () {
    if (fig1.dispose && fig2.dispose) {
        let chartsArr = [];

        chartsArr.push(fig1);
        chartsArr.push(fig2);

        for (let i = 0; i < chartsArr.length; i++) {
            // ECharts随窗口大小改变而自适应
            chartsArr[i].resize();
        }
    }
    if (fig3.dispose) {
        // ECharts随窗口大小改变而自适应
        fig3.resize();
    }
    if (fig4.dispose) {
        // ECharts随窗口大小改变而自适应
        fig4.resize();
    }
};

function isInArray(arr, val) {
    let testStr = ',' + arr.join(",") + ",";
    return testStr.indexOf("," + val + ",") === -1
}

// tooltip: {
//     formatter : function (params) {
//         console.log(params[0].value);
//     },
//     backgroundColor: "gray",
//     position: function (point, params, dom, rect, size) {
//         // 鼠标坐标和提示框位置的参考坐标系是：以外层div的左上角那一点为原点，x轴向右，y轴向下
//         // 提示框位置
//         let x = 0; // x坐标位置
//         let y = 0; // y坐标位置
//
//         // 当前鼠标位置
//         let pointX = point[0];
//         let pointY = point[1];
//
//         // 外层div大小
//         // let viewWidth = size.viewSize[0];
//         // let viewHeight = size.viewSize[1];
//
//         // 提示框大小
//         let boxWidth = size.contentSize[0];
//         let boxHeight = size.contentSize[1];
//
//         // boxWidth > pointX 说明鼠标左边放不下提示框
//         if (boxWidth > pointX) {
//         x = 5;
//         } else { // 左边放的下
//         x = pointX;
//         }
//
//         // boxHeight > pointY 说明鼠标上边放不下提示框
//         if (boxHeight > pointY) {
//         y = 5;
//         } else { // 上边放得下
//         y = pointY;
//         }
//
//         return [x, y];
//     },
// }

// fig3.getZr().on('click', function (params) {
//     // console.log(params);
//     let point = [params.offsetX, params.offsetY];
//     if (fig3.containPixel({seriesIndex: 0}, point)) {
//         let xIndex = fig3.convertFromPixel({seriesIndex: 0}, point)[0];
//         let op = fig3.getOption();
//         // console.log(op);
//         let allxIndex = op.series[0].data.map((x) => x.value[0]);
//         let diff = allxIndex.map((x) => Math.abs(x-xIndex));
//         let closest = Math.min.apply(null, diff);
//         let idx = diff.indexOf(closest);
//         let name = op.series[0].data[idx].value[0];
//         let value = op.series[0].data[idx].value[1];
//         fig3.dispatchAction({
//             type: 'showTip',
//             seriesIndex: 0,//这行不能省
//             dataIndex: idx
//         });
//         document.getElementById('time_info').innerHTML = name + ': ' + value;
//     }
// });
