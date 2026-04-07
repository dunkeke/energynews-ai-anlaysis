/**
 * 能源化工新闻分析软件 - 可视化配置文件
 * =================================================
 * 本文件包含所有图表的配置和主题设置
 */

// ==================== 主题配置 ====================
export const chartTheme = {
    // 配色方案
    color: [
        '#5470c6',  // 主色-蓝
        '#91cc75',  // 辅助色-绿
        '#fac858',  // 辅助色-黄
        '#ee6666',  // 辅助色-红
        '#73c0de',  // 辅助色-青
        '#3ba272',  // 辅助色-深绿
        '#fc8452',  // 辅助色-橙
        '#9a60b4',  // 辅助色-紫
        '#ea7ccc'   // 辅助色-粉
    ],
    
    // 背景色
    backgroundColor: 'transparent',
    
    // 文本样式
    textStyle: {
        fontFamily: 'Microsoft YaHei, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        fontSize: 12,
        color: '#333'
    },
    
    // 标题样式
    title: {
        textStyle: {
            fontSize: 16,
            fontWeight: 'bold',
            color: '#1a1a1a'
        },
        subtextStyle: {
            fontSize: 12,
            color: '#666'
        }
    },
    
    // 图例样式
    legend: {
        bottom: 0,
        textStyle: {
            fontSize: 12,
            color: '#666'
        },
        itemWidth: 14,
        itemHeight: 14
    },
    
    // 提示框样式
    tooltip: {
        backgroundColor: 'rgba(50, 50, 50, 0.9)',
        borderColor: '#333',
        borderWidth: 0,
        textStyle: {
            color: '#fff',
            fontSize: 12
        },
        padding: [10, 15],
        borderRadius: 4
    },
    
    // 坐标轴样式
    categoryAxis: {
        axisLine: {
            lineStyle: { color: '#ccc' }
        },
        axisTick: {
            lineStyle: { color: '#ccc' }
        },
        axisLabel: {
            color: '#666'
        },
        splitLine: {
            show: false
        }
    },
    
    valueAxis: {
        axisLine: {
            show: false
        },
        axisTick: {
            show: false
        },
        axisLabel: {
            color: '#666'
        },
        splitLine: {
            lineStyle: {
                color: '#eee',
                type: 'dashed'
            }
        }
    }
};

// ==================== 评分颜色映射 ====================
export const scoreColorMap = {
    strongBullish: {
        min: 80,
        max: 100,
        label: '强烈看涨',
        color: '#00C853',
        gradient: ['#00C853', '#64DD17'],
        textColor: '#fff'
    },
    bullish: {
        min: 65,
        max: 80,
        label: '看涨',
        color: '#69F0AE',
        gradient: ['#69F0AE', '#00C853'],
        textColor: '#fff'
    },
    mildBullish: {
        min: 55,
        max: 65,
        label: '偏看涨',
        color: '#B2FF59',
        gradient: ['#B2FF59', '#69F0AE'],
        textColor: '#333'
    },
    neutral: {
        min: 45,
        max: 55,
        label: '中性',
        color: '#FFD54F',
        gradient: ['#FFD54F', '#FFC107'],
        textColor: '#333'
    },
    mildBearish: {
        min: 35,
        max: 45,
        label: '偏看跌',
        color: '#FF8A65',
        gradient: ['#FF8A65', '#FF5722'],
        textColor: '#fff'
    },
    bearish: {
        min: 20,
        max: 35,
        label: '看跌',
        color: '#FF5252',
        gradient: ['#FF5252', '#F44336'],
        textColor: '#fff'
    },
    strongBearish: {
        min: 0,
        max: 20,
        label: '强烈看跌',
        color: '#D32F2F',
        gradient: ['#D32F2F', '#B71C1C'],
        textColor: '#fff'
    }
};

// 获取评分对应的颜色配置
export function getScoreColorConfig(score) {
    for (const key in scoreColorMap) {
        const config = scoreColorMap[key];
        if (score >= config.min && score <= config.max) {
            return config;
        }
    }
    return scoreColorMap.neutral;
}

// ==================== 雷达图配置 ====================
export const radarChartConfig = {
    dimensions: ['基本面', '宏观面', '情绪面', '技术面', '地缘风险'],
    maxValue: 100,
    minValue: 0,
    indicator: [
        { name: '基本面', max: 100 },
        { name: '宏观面', max: 100 },
        { name: '情绪面', max: 100 },
        { name: '技术面', max: 100 },
        { name: '地缘风险', max: 100 }
    ],
    shape: 'polygon',
    splitNumber: 5,
    axisName: {
        color: '#333',
        fontSize: 12,
        fontWeight: 'bold'
    },
    splitArea: {
        areaStyle: {
            color: ['rgba(84, 112, 198, 0.05)', 'rgba(84, 112, 198, 0.1)',
                    'rgba(84, 112, 198, 0.15)', 'rgba(84, 112, 198, 0.2)',
                    'rgba(84, 112, 198, 0.25)']
        }
    },
    axisLine: {
        lineStyle: {
            color: 'rgba(84, 112, 198, 0.3)'
        }
    },
    splitLine: {
        lineStyle: {
            color: 'rgba(84, 112, 198, 0.3)'
        }
    }
};

// ==================== 趋势图配置 ====================
export const trendChartConfig = {
    timeRanges: [
        { label: '1H', value: 1, unit: 'hour' },
        { label: '6H', value: 6, unit: 'hour' },
        { label: '1D', value: 1, unit: 'day' },
        { label: '3D', value: 3, unit: 'day' },
        { label: '1W', value: 7, unit: 'day' },
        { label: '2W', value: 14, unit: 'day' },
        { label: '1M', value: 30, unit: 'day' },
        { label: '3M', value: 90, unit: 'day' }
    ],
    defaultRange: '1W',
    indicators: [
        { key: 'composite', label: '综合评分', color: '#5470c6', lineWidth: 3 },
        { key: 'fundamental', label: '基本面', color: '#91cc75', lineWidth: 2, lineType: 'dashed' },
        { key: 'sentiment', label: '情绪面', color: '#fac858', lineWidth: 2, lineType: 'dashed' },
        { key: 'technical', label: '技术面', color: '#ee6666', lineWidth: 2, lineType: 'dashed' },
        { key: 'macro', label: '宏观面', color: '#73c0de', lineWidth: 2, lineType: 'dashed' }
    ],
    annotations: true
};

// ==================== 热力图配置 ====================
export const heatmapConfig = {
    xAxis: ['基本面', '宏观面', '情绪面', '技术面', '地缘风险'],
    yAxis: ['WTI', 'Brent', 'HH', 'JKM', 'TTF', 'PG', 'CP', 'MB', 'FEI'],
    visualMap: {
        min: 0,
        max: 100,
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: '5%',
        inRange: {
            color: [
                '#313695',  // 深蓝 (0分)
                '#4575b4',
                '#74add1',
                '#abd9e9',
                '#e0f3f8',
                '#fee090',
                '#fdae61',
                '#f46d43',
                '#d73027'   // 深红 (100分)
            ]
        }
    }
};

// ==================== 风险仪表盘配置 ====================
export const riskGaugeConfig = {
    min: 0,
    max: 15,
    splitNumber: 5,
    axisLine: {
        lineStyle: {
            width: 20,
            color: [
                [0.33, '#67e8f9'],  // 低风险 - 青色
                [0.66, '#fbbf24'],  // 中风险 - 黄色
                [1, '#f87171']      // 高风险 - 红色
            ]
        }
    },
    pointer: {
        length: '60%',
        width: 6,
        itemStyle: {
            color: '#333'
        }
    },
    axisTick: {
        distance: -25,
        splitNumber: 5,
        lineStyle: {
            width: 2,
            color: '#999'
        }
    },
    splitLine: {
        distance: -32,
        length: 10,
        lineStyle: {
            width: 3,
            color: '#999'
        }
    },
    axisLabel: {
        distance: -15,
        color: '#666',
        fontSize: 12,
        formatter: function(value) {
            if (value <= 5) return '低';
            if (value <= 10) return '中';
            return '高';
        }
    },
    detail: {
        valueAnimation: true,
        formatter: '{value}',
        color: 'auto',
        fontSize: 30,
        fontWeight: 'bold',
        offsetCenter: [0, '30%']
    }
};

// ==================== 预警等级配置 ====================
export const alertLevelConfig = {
    red: {
        label: '红色预警',
        color: '#f44336',
        bgColor: 'rgba(244, 67, 54, 0.1)',
        icon: '🔴',
        priority: 1,
        responseTime: '即时'
    },
    orange: {
        label: '橙色预警',
        color: '#ff9800',
        bgColor: 'rgba(255, 152, 0, 0.1)',
        icon: '🟠',
        priority: 2,
        responseTime: '15分钟内'
    },
    yellow: {
        label: '黄色预警',
        color: '#ffc107',
        bgColor: 'rgba(255, 193, 7, 0.1)',
        icon: '🟡',
        priority: 3,
        responseTime: '1小时内'
    },
    blue: {
        label: '蓝色预警',
        color: '#2196f3',
        bgColor: 'rgba(33, 150, 243, 0.1)',
        icon: '🔵',
        priority: 4,
        responseTime: '日报提示'
    }
};

// ==================== 品种配置 ====================
export const productConfig = {
    crude_wti: {
        name: 'WTI原油',
        symbol: 'WTI',
        exchange: 'NYMEX',
        unit: '美元/桶',
        decimals: 2
    },
    crude_brent: {
        name: 'Brent原油',
        symbol: 'Brent',
        exchange: 'ICE',
        unit: '美元/桶',
        decimals: 2
    },
    gas_hh: {
        name: '亨利港天然气',
        symbol: 'HH',
        exchange: 'NYMEX',
        unit: '美元/MMBtu',
        decimals: 3
    },
    gas_jkm: {
        name: '日韩基准LNG',
        symbol: 'JKM',
        exchange: 'Platts',
        unit: '美元/MMBtu',
        decimals: 3
    },
    gas_ttf: {
        name: '荷兰天然气',
        symbol: 'TTF',
        exchange: 'ICE',
        unit: '欧元/MWh',
        decimals: 2
    },
    lpg_pg: {
        name: '丙烷(PG)',
        symbol: 'PG',
        exchange: '国内市场',
        unit: '元/吨',
        decimals: 0
    },
    lpg_cp: {
        name: '沙特CP',
        symbol: 'CP',
        exchange: 'Saudi Aramco',
        unit: '美元/吨',
        decimals: 0
    },
    lpg_mb: {
        name: '蒙特贝尔维尤',
        symbol: 'MB',
        exchange: 'OPIS',
        unit: '美分/加仑',
        decimals: 3
    },
    lpg_fei: {
        name: '远东指数',
        symbol: 'FEI',
        exchange: 'CP/FEI',
        unit: '美元/吨',
        decimals: 0
    }
};

// ==================== ECharts 图表选项生成器 ====================

/**
 * 生成雷达图选项
 */
export function generateRadarOption(data, productColors) {
    return {
        title: {
            text: '多维度评分对比',
            left: 'center'
        },
        tooltip: {
            trigger: 'item'
        },
        legend: {
            data: data.map(d => d.name),
            bottom: 0
        },
        radar: radarChartConfig,
        series: [{
            type: 'radar',
            data: data.map((d, i) => ({
                value: d.values,
                name: d.name,
                itemStyle: {
                    color: productColors[i % productColors.length]
                },
                areaStyle: {
                    opacity: 0.3
                },
                lineStyle: {
                    width: 2
                }
            }))
        }]
    };
}

/**
 * 生成趋势图选项
 */
export function generateTrendOption(data, indicators) {
    const series = indicators.map(ind => ({
        name: ind.label,
        type: 'line',
        smooth: true,
        data: data.map(d => ({
            name: d.timestamp,
            value: [d.timestamp, d[ind.key]]
        })),
        lineStyle: {
            width: ind.lineWidth,
            type: ind.lineType || 'solid'
        },
        itemStyle: {
            color: ind.color
        },
        areaStyle: ind.key === 'composite' ? {
            opacity: 0.2,
            color: ind.color
        } : undefined
    }));
    
    return {
        title: {
            text: '评分趋势分析',
            left: 'center'
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            }
        },
        legend: {
            data: indicators.map(i => i.label),
            bottom: 0
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '15%',
            containLabel: true
        },
        xAxis: {
            type: 'time',
            boundaryGap: false
        },
        yAxis: {
            type: 'value',
            min: 0,
            max: 100,
            splitLine: {
                lineStyle: {
                    type: 'dashed'
                }
            }
        },
        series
    };
}

/**
 * 生成热力图选项
 */
export function generateHeatmapOption(data, xAxis, yAxis) {
    return {
        title: {
            text: '品种维度评分热力图',
            left: 'center'
        },
        tooltip: {
            position: 'top',
            formatter: function(params) {
                return `${yAxis[params.value[1]]} - ${xAxis[params.value[0]]}<br/>评分: ${params.value[2]}`;
            }
        },
        grid: {
            height: '70%',
            top: '10%'
        },
        xAxis: {
            type: 'category',
            data: xAxis,
            splitArea: {
                show: true
            }
        },
        yAxis: {
            type: 'category',
            data: yAxis,
            splitArea: {
                show: true
            }
        },
        visualMap: heatmapConfig.visualMap,
        series: [{
            name: '评分',
            type: 'heatmap',
            data: data,
            label: {
                show: true,
                formatter: '{c}'
            },
            emphasis: {
                itemStyle: {
                    shadowBlur: 10,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
            }
        }]
    };
}

/**
 * 生成仪表盘选项
 */
export function generateGaugeOption(value, title) {
    return {
        series: [{
            type: 'gauge',
            startAngle: 180,
            endAngle: 0,
            min: riskGaugeConfig.min,
            max: riskGaugeConfig.max,
            splitNumber: riskGaugeConfig.splitNumber,
            itemStyle: {
                color: '#FF6B6B'
            },
            progress: {
                show: true,
                width: 20
            },
            pointer: riskGaugeConfig.pointer,
            axisLine: riskGaugeConfig.axisLine,
            axisTick: riskGaugeConfig.axisTick,
            splitLine: riskGaugeConfig.splitLine,
            axisLabel: riskGaugeConfig.axisLabel,
            detail: {
                ...riskGaugeConfig.detail,
                valueAnimation: true,
                formatter: '{value}'
            },
            data: [{
                value: value,
                name: title
            }]
        }]
    };
}

// ==================== 导出配置 ====================
export default {
    chartTheme,
    scoreColorMap,
    getScoreColorConfig,
    radarChartConfig,
    trendChartConfig,
    heatmapConfig,
    riskGaugeConfig,
    alertLevelConfig,
    productConfig,
    generateRadarOption,
    generateTrendOption,
    generateHeatmapOption,
    generateGaugeOption
};
