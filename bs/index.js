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
});

//注意：折叠面板 依赖 element 模块，否则无法进行功能性操作
//注意：选项卡 依赖 element 模块，否则无法进行功能性操作
layui.use('element', function () {
    let element = layui.element;
    // 监听折叠
    element.on('collapse(params)', function(data){
    });
    // 监听Tab切换
    element.on('tab(spectrum)', function(data){
    });
});

$(document).ready(function () {
    // 标识哪个按钮被点击了
    flag = 0;
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
    document.getElementById('tree1').style.display='none';
    document.getElementById('tree2').style.display='none';
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
    let now = getDate();
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
    // addEventListener() 方法用于向指定元素添加事件句柄
    document.getElementById("fig-t").addEventListener('contextmenu', function (e) {
        // event.preventDefault() 方法阻止元素发生默认的行为
        e.preventDefault();
    }, false);
    // addEventListener() 方法用于向指定元素添加事件句柄
    document.getElementById("fig-f").addEventListener('contextmenu', function (e) {
        // event.preventDefault() 方法阻止元素发生默认的行为
        e.preventDefault();
    }, false);
    // addEventListener() 方法用于向指定元素添加事件句柄
    document.getElementById("fig-e").addEventListener('contextmenu', function (e) {
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
    // 必须使用#id进行选择才有效果
    $('#wind_turbine').change(function () {
        let treeObj1 = $.fn.zTree.getZTreeObj("tree1");
        if (treeObj1) {
            treeObj1.destroy()
        }
        let treeObj2 = $.fn.zTree.getZTreeObj("tree2");
        if (treeObj2) {
            treeObj2.destroy()
        }
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
        // 设置折叠面板标题
        document.getElementById('colla-title').innerHTML = '时域频域包络图';
        layui.use('element', function () {
            let element = layui.element;
            element.render('collapse');
        });
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
        document.getElementById('tree1').style.display='none';
        document.getElementById('tree2').style.display='none';
    });
});

$(document).ready(function () {
    $("input[name=trend]").click(function () {
        // 设置点击标识为2
        flag = 2;
        // 设置折叠面板标题
        document.getElementById('colla-title').innerHTML = '趋势图';
        layui.use('element', function () {
            let element = layui.element;
            element.render('collapse');
        });
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
        document.getElementById('tree1').style.display='none';
        document.getElementById('tree2').style.display='none';
    });
});

function tfe () {
    let ts_checked = $('#ts').prop('checked');
    let freq_checked = $('#freq').prop('checked');
    let env_checked = $('#env').prop('checked');
    if (ts_checked && (typeof fig_t) !== "undefined") {
        if (fig_t.dispose) {
            fig_t.dispose();
        }
    }
    if (freq_checked && (typeof fig_f) !== "undefined") {
        if (fig_f.dispose) {
            fig_f.dispose();
        }
    }
    if (env_checked && (typeof fig_e) !== "undefined") {
        if (fig_e.dispose) {
            fig_e.dispose();
        }
    }
    // 绘图div父容器的宽度
    let w = $('.figure').width();
    $('#fig-t').css('width', w); // 获取父容器的宽度直接赋值给图表以达到宽度100%的效果
    $('#fig-f').css('width', w); // 获取父容器的宽度直接赋值给图表以达到宽度100%的效果
    $('#fig-e').css('width', w); // 获取父容器的宽度直接赋值给图表以达到宽度100%的效果
    fig_t = echarts.init(document.getElementById('fig-t'), 'white', {renderer: 'canvas'});
    fig_f = echarts.init(document.getElementById('fig-f'), 'white', {renderer: 'canvas'});
    fig_e = echarts.init(document.getElementById('fig-e'), 'white', {renderer: 'canvas'});
    let farm_name = $('#farm').find('option:selected').text();
    let wind_turbine_name = $('#wind_turbine').find('option:selected').text();
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
            'sampling_time': sn2[0]['name'].split(':')[0],
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
                let data_length = data['time_series'].length;
                let fs = data['fs'];
                let step = Math.round((data_length / fs) / data_length * 1000000) / 1000000;
                let new_data = [];
                for (let i in data['time_series']) {
                    new_data.push([step * parseInt(i), data['time_series'][i]])
                }
                data['time_series'] = new_data;
                let option_ts = {};
                setOption_tfe(fig_t, option_ts, '时域图', 'time_series', data, [wind_turbine_name]);
                // 解决echarts中click事件重复执行的问题
                fig_t.off('click');
                // 增加自定义参数而不覆盖原本的默认参数
                fig_t.on('click', (params) => {
                    markPoint(fig_t, params);
                });
                markPoint_batch_deletion(fig_t);
                fig_t.on('contextmenu', (params) => { deletemarkPoint (fig_t, params) });

                let option_freq = {};
                setOption_tfe(fig_f, option_freq, '频域图', 'freq', data, [wind_turbine_name]);
                // 解决echarts中click事件重复执行的问题
                fig_f.off('click');
                // 增加自定义参数而不覆盖原本的默认参数
                fig_f.on('click', (params) => {
                    markPoint(fig_f, params);
                    freqMulti(fig_f, params);
                });
                markPoint_batch_deletion(fig_f);
                freqMulti_batch_deletion(fig_f);
                fig_f.on('contextmenu', (params) => { deletemarkPoint (fig_f, params) });

                let option_envelope = {};
                setOption_tfe(fig_e, option_envelope, '包络图', 'envelope', data, [wind_turbine_name]);
                // 解决echarts中click事件重复执行的问题
                fig_e.off('click');
                // 增加自定义参数而不覆盖原本的默认参数
                fig_e.on('click', (params) => {
                    markPoint(fig_e, params);
                    freqMulti(fig_e, params);
                });
                markPoint_batch_deletion(fig_e);
                freqMulti_batch_deletion(fig_e);
                fig_e.on('contextmenu', (params) => { deletemarkPoint (fig_e, params) });
            }
        });
    }
}

function trend () {
    if (fig1.dispose) {
        fig1.dispose();
    }
    if (fig2.dispose) {
        fig2.dispose();
    }
    if (fig3.dispose) {
        fig3.dispose();
    }
    if (fig4.dispose) {
        fig4.dispose();
    }
    // 绘图div父容器的宽度
    let w = $('.figure').width();
    $('#fig1').css('width', w); // 获取父容器的宽度直接赋值给图表以达到宽度100%的效果
    $('#fig2').css('width', w); // 获取父容器的宽度直接赋值给图表以达到宽度100%的效果
    $('#fig3').css('width', w); // 获取父容器的宽度直接赋值给图表以达到宽度100%的效果
    $('#fig4').css('width', w); // 获取父容器的宽度直接赋值给图表以达到宽度100%的效果
    fig1 = echarts.init(document.getElementById('fig1'), 'white', {renderer: 'canvas'});
    fig2 = echarts.init(document.getElementById('fig2'), 'white', {renderer: 'canvas'});
    fig3 = echarts.init(document.getElementById('fig3'), 'white', {renderer: 'canvas'});
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
        let point_name = sn[0]['name'];
        let dataset = {'farm_name': farm_name,
            'point': point_name,
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
                    let warning_acc = {
                        lineStyle: {
                            color: 'orange'
                        },
                        name: '预警线',
                        yAxis: 0.3
                    };
                    let alarm_acc = {
                        lineStyle: {
                            color: 'red'
                        },
                        name: '报警线',
                        yAxis: 0.5
                    };
                    let warning_vel = {
                        lineStyle: {
                            color: 'orange'
                        },
                        name: '预警线',
                        yAxis: 2.0
                    };
                    let alarm_vel = {
                        lineStyle: {
                            color: 'red'
                        },
                        name: '报警线',
                        yAxis: 3.2
                    };
                    let warning2_acc = {
                        lineStyle: {
                            color: 'orange'
                        },
                        name: '预警线',
                        yAxis: 7.5
                    };
                    let alarm2_acc = {
                        lineStyle: {
                            color: 'red'
                        },
                        name: '报警线',
                        yAxis: 12
                    };
                    let cutoff = '(0.1-10Hz)';

                    if (point_name.indexOf('齿轮箱') !== -1) {
                        warning_vel.yAxis = 3.5;
                        alarm_vel.yAxis = 5.6;
                    }
                    if (point_name.indexOf('发电机') !== -1) {
                        warning_acc.yAxis = 10;
                        alarm_acc.yAxis = 16;
                        warning_vel.yAxis = 6;
                        alarm_vel.yAxis = 10;
                        cutoff = '(10-5000Hz)';
                    }

                    let option_ev = {};
                    setOption_trend(fig1, option_ev, point_name+'有效值'+cutoff, '时间(s)', '加速度(m/s^2)', 'vdi', 'ev', data, wind_turbine_selected);
                    fig1.setOption({
                        series: [{
                            markLine: {
                                silent: true,
                                symbol: 'none',
                                label: {
                                    formatter: '{b}: {c}'
                                },
                                data: [warning_acc, alarm_acc]
                            }
                        }]
                    });
                    // 增加自定义参数而不覆盖原本的默认参数
                    fig1.on('click', (params) => {
                        markPoint(fig1, params);
                        draw(farm_name, point_name, 'vdi', data, params);
                    });
                    markPoint_batch_deletion(fig1);
                    fig1.on('contextmenu', (params) => { deletemarkPoint (fig1, params) });

                    let option_iv = {};
                    setOption_trend(fig2, option_iv, point_name+'烈度(10-1000Hz)', '时间(s)', '速度(m/s)', 'vdi', 'iv', data, wind_turbine_selected);
                    fig2.setOption({
                        series: [{
                            markLine: {
                                silent: true,
                                symbol: 'none',
                                label: {
                                    formatter: '{b}: {c}'
                                },
                                data: [warning_vel, alarm_vel]
                            }
                        }]
                    });
                    fig2.on('click', (params) => {
                        markPoint(fig2, params);
                        draw(farm_name, point_name, 'vdi', data, params);
                    });
                    markPoint_batch_deletion(fig2);
                    fig2.on('contextmenu', (params) => { deletemarkPoint (fig2, params) });

                    let option_ev2 = {};
                    setOption_trend(fig3, option_ev2, point_name+'有效值(10-2000Hz)', '时间(s)', '加速度(m/s^2)', 'vdi', 'ev2', data, wind_turbine_selected);
                    if (point_name.indexOf('齿轮箱') !== -1) {
                        fig3.setOption({
                            series: [{
                                markLine: {
                                    silent: true,
                                    symbol: 'none',
                                    label: {
                                        formatter: '{b}: {c}'
                                    },
                                    data: [warning2_acc, alarm2_acc]
                                }
                            }]
                        });
                    }
                    fig3.on('click', (params) => {
                        markPoint(fig3, params);
                        draw(farm_name, point_name, 'vdi', data, params);
                    });
                    markPoint_batch_deletion(fig3);
                    fig3.on('contextmenu', (params) => { deletemarkPoint (fig3, params) });
                }
                if (criterion === '2') {
                    let cutoff = '(0.1-10Hz)';
                    if (point_name.indexOf('发电机') !== -1) {
                        cutoff = '(10-5000Hz)';
                    }
                    let option_k = {};
                    setOption_trend(fig1, option_k, point_name+'峭度'+cutoff, '时间(s)', '峭度', 'dimensionless', 'kurtosisfactor', data, wind_turbine_selected);
                    // 增加自定义参数而不覆盖原本的默认参数
                    fig1.on('click', (params) => {
                        markPoint(fig1, params);
                        draw(farm_name, point_name, 'dimensionless', data, params);
                    });
                    markPoint_batch_deletion(fig1);
                    fig1.on('contextmenu', (params) => { deletemarkPoint (fig1, params) });

                    let option_p = {};
                    setOption_trend(fig2, option_p, point_name+'脉冲因子'+cutoff, '时间(s)', '脉冲因子', 'dimensionless', 'pulsefactor', data, wind_turbine_selected);
                    fig2.on('click', (params) => {
                        markPoint(fig2, params);
                        draw(farm_name, point_name, 'dimensionless', data, params);
                    });
                    markPoint_batch_deletion(fig2);
                    fig2.on('contextmenu', (params) => { deletemarkPoint (fig2, params) });

                    let option_k2 = {};
                    setOption_trend(fig3, option_k2, point_name+'峭度(10-2000Hz)', '时间(s)', '峭度', 'dimensionless', 'kurtosisfactor2', data, wind_turbine_selected);
                    fig3.on('click', (params) => {
                        markPoint(fig3, params);
                        draw(farm_name, point_name, 'dimensionless', data, params);
                    });
                    markPoint_batch_deletion(fig3);
                    fig3.on('contextmenu', (params) => { deletemarkPoint (fig3, params) });

                    let option_p2 = {};
                    setOption_trend(fig4, option_p2, point_name+'脉冲因子(10-2000Hz)', '时间(s)', '脉冲因子', 'dimensionless', 'pulsefactor2', data, wind_turbine_selected);
                    fig4.on('click', (params) => {
                        markPoint(fig4, params);
                        draw(farm_name, point_name, 'dimensionless', data, params);
                    });
                    markPoint_batch_deletion(fig4);
                    fig4.on('contextmenu', (params) => { deletemarkPoint (fig4, params) });
                }
                if (criterion === '3') {
                    let option_rms = {};
                    setOption_trend(fig1, option_rms, point_name+'有效值', '时间(s)', '加速度(m/s^2)', 'narrowband', 'value_rms', data, wind_turbine_selected);
                    // 增加自定义参数而不覆盖原本的默认参数
                    fig1.on('click', (params) => {
                        markPoint(fig1, params);
                        draw(farm_name, point_name, 'narrowband', data, params);
                    });
                    markPoint_batch_deletion(fig1);
                    fig1.on('contextmenu', (params) => { deletemarkPoint (fig1, params) });

                    let option_kurtosis = {};
                    setOption_trend(fig2, option_kurtosis, point_name+'峭度', '时间(s)', '峭度', 'narrowband', 'value_kurtosis', data, wind_turbine_selected);
                    fig2.on('click', (params) => {
                        markPoint(fig2, params);
                        draw(farm_name, point_name, 'narrowband', data, params);
                    });
                    markPoint_batch_deletion(fig2);
                    fig2.on('contextmenu', (params) => { deletemarkPoint (fig2, params) });
                }
            }
        });
    }
}

// 获取分析结果数据集
function getDataset() {
    let farm_name = $('#farm').find('option:selected').text();
    let wind_turbine_name = $('#wind_turbine').find('option:selected').text();
    let treeObj1 = $.fn.zTree.getZTreeObj("tree1");
    let treeObj2 = $.fn.zTree.getZTreeObj("tree2");
    // 当前选中节点
    let sn1 = treeObj1.getSelectedNodes();
    let sn2 = treeObj2.getSelectedNodes();
    let point_name = sn1[0]['name'];
    let sampling_time = sn2[0]['name'].split(':')[0];
    let analyst = $('#analyst').find('option:selected').text();
    let ts = $('#ts-analysis').val();
    let freq = $('#freq-analysis').val();
    let env = $('#env-analysis').val();
    let trend = $('#trend-analysis').val();
    let level = $('#failure-level').find('option:selected').text();
    let img = fig_t.getDataURL({
        pixelRatio: 2,
        backgroundColor: '#fff'
    });

    return {
        'farm_name': farm_name,
        'wind_turbine_name': wind_turbine_name,
        'point_name': point_name,
        'sampling_time': sampling_time,
        'analyst': analyst,
        'ts': ts,
        'freq': freq,
        'env': env,
        'trend': trend,
        'level': level,
        'img': img,
    };
}

$(document).ready(function () {
    $("input[id=preview]").click(function () {
        let dataset = getDataset();

        iframe('/analysis_results', '分析结果', dataset);
    });

    $("input[id=submit]").click(function () {
        let dataset = getDataset();

        layui.use('layer', function () {
            let layer = layui.layer;

            layer.prompt({title: '输入口令，并确认', formType: 1}, function(pass, index){
                $.ajax({
                    url: "/getpass",
                    type: "POST",
                    dataType: "json",
                    success: function (data) {
                        if (pass === data['pass']) {
                            layer.close(index);
                            $.ajax({
                                url: "/analysis_results",
                                type: "POST",
                                data: dataset,
                                dataType: "json",
                                success: function (data) {
                                    if (data['status'] === 'success') {
                                        msg('提交成功！');
                                    }
                                }
                            });
                        }
                    }
                });
            });
        });
    });
});

window.onresize = function () {
    // 绘图div父容器的宽度
    let w = $('.figure').width();
    $('#fig1').css('width', w); // 获取父容器的宽度直接赋值给图表以达到宽度100%的效果
    $('#fig2').css('width', w); // 获取父容器的宽度直接赋值给图表以达到宽度100%的效果
    $('#fig3').css('width', w); // 获取父容器的宽度直接赋值给图表以达到宽度100%的效果
    $('#fig4').css('width', w); // 获取父容器的宽度直接赋值给图表以达到宽度100%的效果
    $('#fig-t').css('width', w); // 获取父容器的宽度直接赋值给图表以达到宽度100%的效果
    $('#fig-f').css('width', w); // 获取父容器的宽度直接赋值给图表以达到宽度100%的效果
    $('#fig-e').css('width', w); // 获取父容器的宽度直接赋值给图表以达到宽度100%的效果
    if ((typeof fig1) !== "undefined" && fig1.dispose) {
        // ECharts随窗口大小改变而自适应
        fig1.resize();
    }
    if ((typeof fig2) !== "undefined" && fig2.dispose) {
        // ECharts随窗口大小改变而自适应
        fig2.resize();
    }
    if ((typeof fig3) !== "undefined" && fig3.dispose) {
        // ECharts随窗口大小改变而自适应
        fig3.resize();
    }
    if ((typeof fig4) !== "undefined" && fig4.dispose) {
        // ECharts随窗口大小改变而自适应
        fig4.resize();
    }
    if ((typeof fig_t) !== "undefined" && fig_t.dispose) {
        // ECharts随窗口大小改变而自适应
        fig_t.resize();
    }
    if ((typeof fig_f) !== "undefined" && fig_f.dispose) {
        // ECharts随窗口大小改变而自适应
        fig_f.resize();
    }
    if ((typeof fig_e) !== "undefined" && fig_e.dispose) {
        // ECharts随窗口大小改变而自适应
        fig_e.resize();
    }
};

