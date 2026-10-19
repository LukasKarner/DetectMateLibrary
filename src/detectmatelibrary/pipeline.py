
from detectmatelibrary.common.core import CoreComponent, CoreConfig
from detectmatelibrary.common.detector import CoreDetectorConfig
from detectmatelibrary.common.parser import CoreParserConfig

from detectmatelibrary.utils.data_buffer import ArgsBuffer, BufferMode

import detectmatelibrary.schemas as sc

from typing import Any, Optional, overload, override
from pydantic import Field


class PipelineConfig(CoreConfig):
    component_type: str = Field(default="main_pipeline", description="<$IGNORE$>")
    method_type: str = Field(default="pipeline", description="<$IGNORE$>")

    do_parsing: bool = Field(default=True, description="Run parser in the pipeline.")
    do_aggregation: bool = Field(default=True, description="Run aggregator in the pipeline.")

    parser: CoreParserConfig | dict[str, Any] | None = Field(
        default=None, description="Parser configuration use, if do_parsing=False keep empty."
    )
    detectors: list[CoreDetectorConfig | dict[str, Any]] | None = Field(
        default=None, description="Detectors configuration use."
    )
    aggregators: CoreParserConfig | dict[str, Any] | None = Field(
        default=None, description="Aggregator configuration use, if do_aggregation=False keep empty."
    )


def _select_input(config: PipelineConfig) -> type[sc.BaseSchema]:
    return sc.LogSchema if config.do_parsing else sc.ParserSchema


def _select_output(config: PipelineConfig) -> type[sc.BaseSchema]:
    return sc.DetectorSchema if config.do_aggregation else sc.AggregateSchema


class Pipeline(CoreComponent):
    def __init__(
        self,
        name: str = "MainPipeline",
        buffer_mode: BufferMode = BufferMode.WINDOW,
        buffer_size: Optional[int] = 1,
        config: PipelineConfig | dict[str, Any] = PipelineConfig(),
    ) -> None:
        if isinstance(config, dict):
            config = PipelineConfig.from_dict(config, name)

        super().__init__(
            name=name,
            type_=config.method_type,
            config=config,
            args_buffer=ArgsBuffer(mode=buffer_mode, size=buffer_size),
            input_schema=_select_input(config),
            output_schema=_select_output(config),
        )
        self.config: PipelineConfig

    @overload    # type: ignore
    @override
    def run(
        self,
        input_: list[sc.LogSchema] | sc.LogSchema,
        output_: list[sc.DetectorSchema] | sc.DetectorSchema
    ) -> bool:
        pass

    @overload
    @override
    def run(self, input_: list[sc.LogSchema] | sc.LogSchema,  output_: sc.AggregateSchema) -> bool:
        pass

    @overload
    @override
    def run(
        self,
        input_: list[sc.ParserSchema] | sc.ParserSchema,
        output_: list[sc.DetectorSchema] | sc.DetectorSchema
    ) -> bool:
        pass

    @overload
    @override
    def run(self, input_: list[sc.ParserSchema] | sc.ParserSchema,  output_: sc.AggregateSchema) -> bool:
        pass

    @override
    def run(
        self,
        input_: list[sc.LogSchema] | sc.LogSchema | list[sc.ParserSchema] | sc.ParserSchema,
        output_: list[sc.DetectorSchema] | sc.DetectorSchema | sc.AggregateSchema
    ) -> bool:
        return True
