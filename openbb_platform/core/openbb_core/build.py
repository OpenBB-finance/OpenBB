"""用于构建 OpenBB 平台静态资产的脚本。"""

# flake8: noqa: S603
# pylint: disable=import-outside-toplevel,unused-import
import logging
import subprocess
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def main():
    """构建 OpenBB 平台静态资产。"""
    try:
        logger.info("正在尝试导入 OpenBB 包...\n")
        # 尝试在子进程中导入 openbb 并捕获输出
        result = subprocess.run(
            [sys.executable, "-c", "import openbb"],
            capture_output=True,
            text=True,
            check=False,
        )
        logger.info(result.stdout)
        building_found = any(
            line.startswith("Building") for line in result.stdout.splitlines()
        )

        if result.returncode != 0:
            logger.error(result.stderr)

            if not result.stderr.endswith(
                "ModuleNotFoundError: No module named 'openbb'\n"
            ):
                sys.exit(1)
            raise subprocess.CalledProcessError(
                returncode=result.returncode,
                cmd=f"{sys.executable} -c import openbb",
                output=result.stdout,
                stderr=result.stderr,
            )

    except (ModuleNotFoundError, subprocess.CalledProcessError) as exc:
        logger.info(
            "OpenBB 构建包"
            "可能已卸载或损坏。"
            "尝试 `pip uninstall openbb` 并在环境中重新安装 `openbb-core`。\n"
        )
        raise exc from None

    if not building_found:
        logger.info("导入时未构建，正在触重建...\n")
        try:
            import openbb  # noqa

            openbb.build()
        except Exception as e:  # pylint: disable=broad-except
            raise RuntimeError(  # noqa
                "未能构建 OpenBB 平台静态资产。\n"
                f"{e} -> {e.__traceback__.tb_frame.f_code.co_filename}:"  # type:ignore  # pylint: disable=E1101
                f"{e.__traceback__.tb_lineno}"  # type:ignore
                if hasattr(e, "__traceback__")
                and hasattr(e.__traceback__, "tb_frame")  # type:ignore
                and hasattr(
                    e.__traceback__.tb_frame,  # type:ignore
                    "f_code",
                )
                and hasattr(
                    e.__traceback__.tb_frame.f_code,  # type:ignore  # pylint: disable=E1101
                    "co_filename",
                )
                and hasattr(
                    e.__traceback__,  # type:ignore
                    "tb_lineno",
                )
                else f"未能构建 OpenBB 平台静态资产。\n{e}"
            ) from e
    sys.exit(0)


if __name__ == "__main__":
    main()
