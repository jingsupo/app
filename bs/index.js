// 加载日期与时间组件
layui.use(['laydate'], function () {
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

// 标识哪个按钮被点击了
let flag = 0;

$(document).ready(function () {
    // 初始化隐藏控件
    document.getElementById('criterion_div').style.display='none';
    document.getElementById('farm_div').style.display='none';
    document.getElementById('wind_turbine_div').style.display='none';
    document.getElementById('more_wind_turbine_div').style.display='none';
    document.getElementById('from_time_div').style.display='none';
    document.getElementById('to_time_div').style.display='none';
    document.getElementById('from_rotate_speed_div').style.display='none';
    document.getElementById('to_rotate_speed_div').style.display='none';
    document.getElementById('fig_type_div').style.display='none';
    document.getElementById('cutoff_div').style.display='none';
    document.getElementById('q').style.display='none';
    document.getElementById('query_info').style.display='none';
    document.getElementById('tree1').style.display='none';
    document.getElementById('tree2').style.display='none';
    document.getElementById('fig1_side').style.display='none';
    document.getElementById('fig2_side').style.display='none';
    document.getElementById('fig3_side').style.display='none';
    document.getElementById('fig4_side').style.display='none';
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
    $('#to_time').val(now);
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
    // addEventListener() 方法用于向指定元素添加事件句柄
    document.getElementById("fig4").addEventListener('contextmenu', function (e) {
        // event.preventDefault() 方法阻止元素发生默认的行为
        e.preventDefault();
    }, false);
});

$(document).ready(function () {
    // 必须使用#id进行选择才有效果
    $('#farm').change(function () {
        let treeObj1 = $.fn.zTree.getZTreeObj("tree1");
        if (treeObj1) {
            treeObj1.destroy()
        }
        let treeObj2 = $.fn.zTree.getZTreeObj("tree2");
        if (treeObj2) {
            treeObj2.destroy()
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
                let more_wind_turbine = document.getElementById('more_wind_turbine');
                // 默认清空已经存在的项目
                $("#more_wind_turbine").empty();
                for (let i=0; i < data.length; i++) {
                    more_wind_turbine.options.add(new Option(data[i], i+1));
                }
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
        let from_rotate_speed = $('#from_rotate_speed').val();
        let to_rotate_speed = $('#to_rotate_speed').val();
        if (farm_name === '选择风场' || wind_turbine_name === '选择风机') {
            msg('请先选择相应项目！');
        }
        else if (from_rotate_speed === '' || to_rotate_speed === '') {
            msg('请输入转速！');
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
                    let zTreeObj1;
                    let setting1 = {
                        callback: {
                            onClick: zTreeOnClick1
                        },
                        view: {
                            showLine: false
                        }
                    };
                    let zNodes1 = [];
                    let child1 = [];
                    for (let key in data['point_description']) {
                        child1.push({name:data['point_description'][key]});
                    }
                    zNodes1.push({name:'测点', open:true, children:child1});
                    function zTreeOnClick1(event, treeId, treeNode) {
                        if (flag === 1) {
                            tfe();
                        }
                        if (flag === 2) {
                            trend();
                        }
                    }
                    zTreeObj1 = $.fn.zTree.init($("#tree1"), setting1, zNodes1);
                    // 显示ztree插件
                    document.getElementById('tree1').style.display='';
                    if (flag === 1) {
                        let zTreeObj2;
                        let setting2 = {
                            callback: {
                                onClick: zTreeOnClick2
                            },
                            view: {
                                showLine: false
                            }
                        };
                        let zNodes2 = [];
                        let child2 = [];
                        for (let i=0; i < data['sampling_time'].length; i++) {
                            child2.push({name:data['sampling_time'][i]});
                        }
                        zNodes2.push({name:'采样时间', open:true, children:child2});
                        function zTreeOnClick2(event, treeId, treeNode) {
                            tfe();
                            let treeObj = $.fn.zTree.getZTreeObj("tree2");
                            // 当前选中节点
                            let sn = treeObj.getSelectedNodes();
                            let html = data['rotate_speed'][sn[0].name];
                            document.getElementById('query_info').innerHTML = '转速：' + html;
                        }
                        zTreeObj2 = $.fn.zTree.init($("#tree2"), setting2, zNodes2);
                        // 显示ztree插件
                        document.getElementById('tree2').style.display='';
                    }
                }
            });
        }
    });
});

$(document).ready(function () {
    $("input[name=tfe]").click(function () {
        // 设置点击标识为1
        flag = 1;
        document.getElementById('query_title').innerHTML = '时域频域包络图';
        document.getElementById('criterion_div').style.display='none';
        document.getElementById('farm_div').style.display='';
        document.getElementById('wind_turbine_div').style.display='';
        document.getElementById('more_wind_turbine_div').style.display='none';
        document.getElementById('from_time_div').style.display='';
        document.getElementById('to_time_div').style.display='';
        document.getElementById('from_rotate_speed_div').style.display='';
        document.getElementById('to_rotate_speed_div').style.display='';
        document.getElementById('fig_type_div').style.display='';
        document.getElementById('cutoff_div').style.display='';
        document.getElementById('q').style.display='';
        document.getElementById('query_info').style.display='';
        document.getElementById('tree1').style.display='none';
        document.getElementById('tree2').style.display='none';
    });
});

$(document).ready(function () {
    $("input[name=trend]").click(function () {
        // 设置点击标识为2
        flag = 2;
        document.getElementById('query_title').innerHTML = '趋势图';
        document.getElementById('criterion_div').style.display='';
        document.getElementById('farm_div').style.display='';
        document.getElementById('wind_turbine_div').style.display='none';
        document.getElementById('more_wind_turbine_div').style.display='';
        document.getElementById('from_time_div').style.display='';
        document.getElementById('to_time_div').style.display='';
        document.getElementById('from_rotate_speed_div').style.display='';
        document.getElementById('to_rotate_speed_div').style.display='';
        document.getElementById('fig_type_div').style.display='none';
        document.getElementById('cutoff_div').style.display='none';
        document.getElementById('q').style.display='';
        document.getElementById('query_info').style.display='';
        document.getElementById('tree1').style.display='none';
        document.getElementById('tree2').style.display='none';
    });
});

function tfe () {
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
    let farm_name = $('#farm').find('option:selected').text();
    let wind_turbine_name = $('#wind_turbine').find('option:selected').text();
    let ts_checked = $('#ts').prop('checked');
    let freq_checked = $('#freq').prop('checked');
    let env_checked = $('#env').prop('checked');
    let low_cutoff = $('#low_cutoff').val();
    let high_cutoff = $('#high_cutoff').val();
    let treeObj1 = $.fn.zTree.getZTreeObj("tree1");
    let treeObj2 = $.fn.zTree.getZTreeObj("tree2");
    // 当前选中节点
    let sn1 = treeObj1.getSelectedNodes();
    let sn2 = treeObj2.getSelectedNodes();
    if (sn1.length === 0) {
        msg('请选择测点！');
    }
    else if (sn2.length === 0) {
        msg('请选择采样时间！');
    }
    else if (sn1[0].hasOwnProperty('children') && sn1[0].children.length > 0) {
        msg('请选择子节点！');
    }
    else if (sn2[0].hasOwnProperty('children') && sn2[0].children.length > 0) {
        msg('请选择子节点！');
    }
    else {
        let dataset = {'farm_name': farm_name,
            'wind_turbine_name': wind_turbine_name,
            'point': sn1[0]['name'],
            'sampling_time': sn2[0]['name'],
            'ts_checked': ts_checked,
            'freq_checked': freq_checked,
            'env_checked': env_checked,
            'low_cutoff': low_cutoff,
            'high_cutoff': high_cutoff,
        };
        $.ajax({
            url: "/tfe",
            type: "POST",
            data: dataset,
            dataType: "json",
            beforeSend: function () {
                loading();
            },
            complete: function () {
                setTimeout(function () {
                    layer.closeAll('loading');
                }, 0);
            },
            success: function (data) {
                let option_ts = {};
                setOption_tfe(fig1, option_ts, '时域图', 'time_series', data, [wind_turbine_name]);
                // 增加自定义参数而不覆盖原本的默认参数
                fig1.on('click', (params) => {
                    addmarkPoint (params, fig1);
                });
                fig1.on('contextmenu', (params) => { deletemarkPoint (params, fig1) });

                let option_freq = {};
                setOption_tfe(fig2, option_freq, '频域图', 'freq', data, [wind_turbine_name]);
                // 增加自定义参数而不覆盖原本的默认参数
                fig2.on('click', (params) => {
                    addmarkPoint (params, fig2);
                });
                fig2.on('contextmenu', (params) => { deletemarkPoint (params, fig2) });

                let option_envelope = {};
                setOption_tfe(fig3, option_envelope, '包络图', 'envelope', data, [wind_turbine_name]);
                // 增加自定义参数而不覆盖原本的默认参数
                fig3.on('click', (params) => {
                    addmarkPoint (params, fig3);
                });
                fig3.on('contextmenu', (params) => { deletemarkPoint (params, fig3) });
            }
        });
    }
}

function trend () {
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
    let farm_name = $('#farm').find('option:selected').text();
    let more_wind_turbine = document.getElementById('more_wind_turbine');
    let wind_turbine_selected = [];
    for (let i = 0; i < more_wind_turbine.length; i++) {
        if (more_wind_turbine.options[i].selected) {
            wind_turbine_selected.push(more_wind_turbine[i].text)
        }
    }
    let from_time = $('#from_time').val();
    let to_time = $('#to_time').val();
    let from_rotate_speed = $('#from_rotate_speed').val();
    let to_rotate_speed = $('#to_rotate_speed').val();
    let treeObj1 = $.fn.zTree.getZTreeObj("tree1");
    // 当前选中节点
    let sn = treeObj1.getSelectedNodes();
    if (sn.length === 0) {
        msg('请选择测点！');
    }
    else if (sn[0].hasOwnProperty('children') && sn[0].children.length > 0) {
        msg('请选择子节点！');
    }
    else if (wind_turbine_selected.length === 0) {
        msg('请选择风机！');
    }
    else if (from_rotate_speed === '' || to_rotate_speed === '') {
        msg('请输入转速！');
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
                loading();
            },
            complete: function () {
                setTimeout(function () {
                    layer.closeAll('loading');
                }, 0);
            },
            success: function (data) {
                if (criterion === '1') {
                    let cutoff = '(0.1-10Hz)';
                    if (data['point'].charAt(data['point'].length-1) > 5) {
                        cutoff = '(10-5000Hz)';
                    }
                    let option_ev = {};
                    setOption_trend(fig1, option_ev, sn[0]['name']+'有效值'+cutoff, '时间(s)', '加速度(m/s^2)', 'vdi', 'ev', data, wind_turbine_selected);
                    // 增加自定义参数而不覆盖原本的默认参数
                    fig1.on('click', (params) => {
                        addmarkPoint (params, fig1);
                        draw('tf_1', 'env_1', 'fig1_side', 'low_cutoff_1', 'high_cutoff_1', farm_name, sn, 'vdi', data, params);
                    });
                    fig1.on('contextmenu', (params) => { deletemarkPoint (params, fig1) });

                    let option_ev2 = {};
                    setOption_trend(fig2, option_ev2, sn[0]['name']+'有效值(10-2000Hz)', '时间(s)', '加速度(m/s^2)', 'vdi', 'ev2', data, wind_turbine_selected);
                    fig2.on('click', (params) => {
                        addmarkPoint (params, fig2);
                        draw('tf_2', 'env_2', 'fig2_side', 'low_cutoff_2', 'high_cutoff_2', farm_name, sn, 'vdi', data, params);
                    });
                    fig2.on('contextmenu', (params) => { deletemarkPoint (params, fig2) });

                    let option_iv = {};
                    setOption_trend(fig3, option_iv, sn[0]['name']+'烈度(10-1000Hz)', '时间(s)', '速度(m/s)', 'vdi', 'iv', data, wind_turbine_selected);
                    fig3.on('click', (params) => {
                        addmarkPoint (params, fig3);
                        draw('tf_3', 'env_3', 'fig3_side', 'low_cutoff_3', 'high_cutoff_3', farm_name, sn, 'vdi', data, params);
                    });
                    fig3.on('contextmenu', (params) => { deletemarkPoint (params, fig3) });
                }
                if (criterion === '2') {
                    let cutoff = '(0.1-10Hz)';
                    if (data['point'].charAt(data['point'].length-1) > 5) {
                        cutoff = '(10-5000Hz)';
                    }
                    let option_k = {};
                    setOption_trend(fig1, option_k, sn[0]['name']+'峭度'+cutoff, '时间(s)', '峭度', 'dimensionless', 'kurtosisfactor', data, wind_turbine_selected);
                    // 增加自定义参数而不覆盖原本的默认参数
                    fig1.on('click', (params) => {
                        addmarkPoint (params, fig1);
                        draw('tf_1', 'env_1', 'fig1_side', 'low_cutoff_1', 'high_cutoff_1', farm_name, sn, 'dimensionless', data, params);
                    });
                    fig1.on('contextmenu', (params) => { deletemarkPoint (params, fig1) });

                    let option_p = {};
                    setOption_trend(fig2, option_p, sn[0]['name']+'脉冲因子'+cutoff, '时间(s)', '脉冲因子', 'dimensionless', 'pulsefactor', data, wind_turbine_selected);
                    fig2.on('click', (params) => {
                        addmarkPoint (params, fig2);
                        draw('tf_2', 'env_2', 'fig2_side', 'low_cutoff_2', 'high_cutoff_2', farm_name, sn, 'dimensionless', data, params);
                    });
                    fig2.on('contextmenu', (params) => { deletemarkPoint (params, fig2) });

                    let option_k2 = {};
                    setOption_trend(fig3, option_k2, sn[0]['name']+'峭度(10-2000Hz)', '时间(s)', '峭度', 'dimensionless', 'kurtosisfactor2', data, wind_turbine_selected);
                    fig3.on('click', (params) => {
                        addmarkPoint (params, fig3);
                        draw('tf_3', 'env_3', 'fig3_side', 'low_cutoff_3', 'high_cutoff_3', farm_name, sn, 'dimensionless', data, params);
                    });
                    fig3.on('contextmenu', (params) => { deletemarkPoint (params, fig3) });

                    let option_p2 = {};
                    setOption_trend(fig4, option_p2, sn[0]['name']+'脉冲因子(10-2000Hz)', '时间(s)', '脉冲因子', 'dimensionless', 'pulsefactor2', data, wind_turbine_selected);
                    fig4.on('click', (params) => {
                        addmarkPoint (params, fig4);
                        draw('tf_4', 'env_4', 'fig4_side', 'low_cutoff_4', 'high_cutoff_4', farm_name, sn, 'dimensionless', data, params);
                    });
                    fig4.on('contextmenu', (params) => { deletemarkPoint (params, fig4) });
                }
                if (criterion === '3') {
                    let option_rms = {};
                    setOption_trend(fig1, option_rms, sn[0]['name']+'有效值', '时间(s)', '加速度(m/s^2)', 'narrowband', 'value_rms', data, wind_turbine_selected);
                    // 增加自定义参数而不覆盖原本的默认参数
                    fig1.on('click', (params) => {
                        addmarkPoint (params, fig1);
                        draw('tf_1', 'env_1', 'fig1_side', 'low_cutoff_1', 'high_cutoff_1', farm_name, sn, 'narrowband', data, params);
                    });
                    fig1.on('contextmenu', (params) => { deletemarkPoint (params, fig1) });

                    let option_kurtosis = {};
                    setOption_trend(fig2, option_kurtosis, sn[0]['name']+'峭度', '时间(s)', '峭度', 'narrowband', 'value_kurtosis', data, wind_turbine_selected);
                    fig2.on('click', (params) => {
                        addmarkPoint (params, fig2);
                        draw('tf_2', 'env_2', 'fig2_side', 'low_cutoff_2', 'high_cutoff_2', farm_name, sn, 'narrowband', data, params);
                    });
                    fig2.on('contextmenu', (params) => { deletemarkPoint (params, fig2) });
                }
            }
        });
    }
}

window.onresize = function () {
    if (fig1.dispose) {
        // ECharts随窗口大小改变而自适应
        fig1.resize();
    }
    if (fig2.dispose) {
        // ECharts随窗口大小改变而自适应
        fig2.resize();
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
